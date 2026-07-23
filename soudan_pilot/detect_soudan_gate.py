#!/usr/bin/env python3
"""SOUDAN decision-support gate detector (意思決定支援室 §4 gates).

Mechanically checks a SOUDAN consultation file against the four gates
defined in DRAFT_20260723_decision_support_office_direction.md §4, and the
field-context authority-citation rule against any citing documents:

  (A) 宛先ゲート     -- for_decider present and in {kuro, 丼ちゃん}.
  (B) 完全性ゲート    -- body sections 1..7 present & non-empty; §4 has >=2
                        options. Section 8 (危険) recommended (WARNING if
                        missing). This is what "decision-ready" means.
  (C) 利益相反ゲート  -- if `subject` is a person/AI, none of prepared_by /
                        committed_by / for_decider may equal it (a
                        consultation about クロ cannot be prepared, written,
                        or decided by クロ). L-031 + cross-AI-check.
  (D) 権限ゲート     -- authority must be `none`; and (across citing docs) a
                        soudan_id may appear ONLY in a `related:` field, never
                        in an `authority:` field or a 根拠 section. Naive id
                        presence is NOT a violation -- the FIELD CONTEXT is.

Stdlib only (no PyYAML). Exits non-zero on any VIOLATION so it can gate.
Same discipline as detect_tier_violations.py: no self-reported PASS field
is read; the verdict is reconstructed from the file's structure.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

VIOLATION = "VIOLATION"
WARNING = "WARNING"
INFO = "INFO"

# Person/AI identities that the conflict-of-interest gate applies to.
# Aliases normalise app names to role names.
PERSON_ALIASES = {
    "claude": "kuro", "kuro": "kuro",
    "codex": "codex", "gpt": "codex",
    "gemini": "gura", "gura": "gura",
    "丼ちゃん": "丼ちゃん", "don": "丼ちゃん", "donchan": "丼ちゃん",
}
VALID_DECIDERS = {"kuro", "丼ちゃん"}

SOUDAN_ID_RE = re.compile(r"S-\d{8}-\d+")
HEADING_RE = re.compile(r"^#{1,6}\s*(\d+)\.\s*(.+?)\s*$")


def normalise_person(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.strip().lower()
    for key, role in PERSON_ALIASES.items():
        if key in v:
            return role
    # 丼ちゃん contains no ascii; check raw too
    if "丼" in value:
        return "丼ちゃん"
    return None  # not a recognised person/AI -> CoI gate N/A


@dataclass
class Finding:
    doc: str
    gate: str        # "A" | "B" | "C" | "D"
    code: str
    severity: str
    message: str

    def line(self) -> str:
        return f"{self.severity:9s} ({self.gate}) {self.code}: {self.message}"


@dataclass
class DocResult:
    doc: str
    soudan_id: Optional[str] = None
    findings: List[Finding] = field(default_factory=list)

    @property
    def violations(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == VIOLATION]


def split_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Return (frontmatter dict, body). Minimal YAML: `key: value` lines."""
    fm: Dict[str, str] = {}
    if not text.startswith("---"):
        return fm, text
    end = text.find("\n---", 3)
    if end == -1:
        return fm, text
    block = text[3:end]
    body = text[end + 4:]
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, val = raw.split(":", 1)
        key = key.strip()
        val = val.strip()
        # strip an inline comment that follows whitespace + '#'
        val = re.sub(r"\s+#.*$", "", val).strip()
        fm[key] = val
    return fm, body


def parse_sections(body: str) -> Dict[int, str]:
    """Map numbered heading (## N. ...) -> section content (until next head)."""
    sections: Dict[int, str] = {}
    current: Optional[int] = None
    buf: List[str] = []
    for ln in body.splitlines():
        m = HEADING_RE.match(ln)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = int(m.group(1))
            buf = []
        elif current is not None:
            buf.append(ln)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def count_options(section_text: str) -> int:
    return sum(1 for ln in section_text.splitlines()
               if ln.lstrip().startswith(("- ", "* ")))


def check_soudan(doc: str, text: str) -> DocResult:
    fm, body = split_frontmatter(text)
    res = DocResult(doc=doc, soudan_id=fm.get("soudan_id"))
    f = res.findings

    # (A) addressee
    decider = fm.get("for_decider", "")
    decider_norm = "丼ちゃん" if "丼" in decider else decider.strip().lower()
    if not decider:
        f.append(Finding(doc, "A", "V_A_NO_DECIDER", VIOLATION,
                         "for_decider is missing"))
    elif decider_norm not in {"kuro", "丼ちゃん"}:
        f.append(Finding(doc, "A", "V_A_BAD_DECIDER", VIOLATION,
                         f"for_decider '{decider}' not in {sorted(VALID_DECIDERS)}"))

    # (D) authority must be none (self)
    if fm.get("authority", "").lower() != "none":
        f.append(Finding(doc, "D", "V_D_AUTHORITY_NOT_NONE", VIOLATION,
                         f"authority must be 'none', got {fm.get('authority')!r}"))
    if fm.get("read_policy", "") != "never_first":
        f.append(Finding(doc, "D", "W_D_READ_POLICY", WARNING,
                         "read_policy should be 'never_first'"))

    # (C) conflict of interest -- subject exclusion
    subject = normalise_person(fm.get("subject"))
    if subject is not None:
        for role_field in ("prepared_by", "committed_by", "for_decider"):
            who = normalise_person(fm.get(role_field))
            if who is not None and who == subject:
                f.append(Finding(
                    doc, "C", "V_C_CONFLICT_OF_INTEREST", VIOLATION,
                    f"{role_field}={who} equals subject={subject} "
                    f"(self-adjudication forbidden; route to a different AI)"))

    # (B) completeness -- body sections 1..7 present & non-empty
    sections = parse_sections(body)
    for n in range(1, 8):
        content = sections.get(n)
        if not content:
            f.append(Finding(doc, "B", "V_B_SECTION_MISSING", VIOLATION,
                             f"required body section {n} missing or empty"))
    if 4 in sections and sections[4]:
        n_opt = count_options(sections[4])
        if n_opt < 2:
            f.append(Finding(doc, "B", "V_B_TOO_FEW_OPTIONS", VIOLATION,
                             f"section 4 has {n_opt} option(s); need >=2"))
    if not sections.get(8):
        f.append(Finding(doc, "B", "W_B_NO_RISK_SECTION", WARNING,
                         "section 8 (危険・未確定) recommended but absent"))
    return res


def check_citation(doc: str, text: str) -> DocResult:
    """(D) field-context authority-citation check for a citing document."""
    fm, body = split_frontmatter(text)
    res = DocResult(doc=doc)
    f = res.findings

    ids_in_related = set(SOUDAN_ID_RE.findall(fm.get("related", "")))
    ids_in_authority = set(SOUDAN_ID_RE.findall(fm.get("authority", "")))
    for sid in ids_in_authority:
        f.append(Finding(doc, "D", "V_D_SOUDAN_AS_AUTHORITY", VIOLATION,
                         f"{sid} cited in `authority:` field (only `related:` "
                         f"is allowed)"))

    # 根拠 section / lines in body
    in_konkyo = False
    for ln in body.splitlines():
        h = re.match(r"^#{1,6}\s*(.+)$", ln)
        if h:
            in_konkyo = "根拠" in h.group(1)
            continue
        line_has_konkyo = "根拠" in ln
        for sid in SOUDAN_ID_RE.findall(ln):
            if (in_konkyo or line_has_konkyo) and sid not in ids_in_related:
                f.append(Finding(
                    doc, "D", "V_D_SOUDAN_AS_BASIS", VIOLATION,
                    f"{sid} used as 根拠 in body (only `related:` provenance "
                    f"is allowed)"))
            elif sid in ids_in_related:
                pass  # provenance reference, fine
            else:
                f.append(Finding(doc, "D", "I_D_SOUDAN_MENTION", INFO,
                                 f"{sid} mentioned in body (not related/根拠)"))
    return res


def _print(results: List[DocResult]) -> None:
    for r in results:
        print(f"\n=== {r.doc} ===")
        if r.soudan_id:
            print(f"  soudan_id: {r.soudan_id}")
        if not r.findings:
            print("  findings: none (all gates pass)")
        for fnd in r.findings:
            print(f"  - {fnd.line()}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("soudan", nargs="*", help="SOUDAN .md file(s)")
    ap.add_argument("--citing", action="append", default=[],
                    metavar="FILE", help="citing document to authority-check")
    args = ap.parse_args(argv)

    results: List[DocResult] = []
    for path in args.soudan:
        with open(path, encoding="utf-8") as fh:
            results.append(check_soudan(path, fh.read()))
    for path in args.citing:
        with open(path, encoding="utf-8") as fh:
            results.append(check_citation(path, fh.read()))

    _print(results)
    total = sum(len(r.violations) for r in results)
    print(f"\nTOTAL VIOLATIONS: {total} across {len(results)} document(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
