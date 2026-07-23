#!/usr/bin/env python3
"""Subagent-tier discipline violation detector.

Reference: DIRECTIVE_20260714_subagent_efficiency.md 補則2 (L-034,
"サブagent格下原則"). The rule, in short:

  1. A subagent's model must be same-or-lower tier than the supervising
     parent session's model; the DEFAULT is at least one tier lower.
  2. Spawning a HIGHER-tier subagent than the parent is an "escalation
     signal" -- doing it silently inverts the command structure and is a
     violation. It is only legitimate when explicitly declared as an
     escalation.
  3. Two exceptions (each needs a one-line reason on the spawn):
        (a) parent is already on the cheapest tier -> same tier allowed;
        (b) capability-specialised task (e.g. image gen) -> pick by
            capability, not tier.
  4. Subagent output is trusted via machine/evidence review, not model
     prestige.

DIRECTION 20260723a D2 asks, for every spawn, whether the parent:
  (a) declared a model table before spawning,
  (b) made the model explicit and (by default) one tier down,
  (c) reviewed the subagent output with cited evidence.

CRITICAL design constraint from D2: "親の自己申告PASSは不可" -- a parent
claiming it complied is not acceptable. This detector therefore reads NO
"pass"/"compliant" field. It reconstructs compliance purely from the
structural events in the session log (presence of a model-table event,
the model attached to each spawn, the tier arithmetic, and whether a
review event with non-empty citations references the spawn).

The tool is stdlib-only (no third-party deps) and exits non-zero when any
VIOLATION (not merely a WARNING) is found, so it can gate CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

# --- Model tier map -------------------------------------------------------
#
# Higher number == higher tier (more capable / more expensive). This map is
# ORG-SPECIFIC to the donzlab command structure, where Fable5 is the top
# adjudication model (L-031) and Opus sits at the CEO-代行/COO tier. It is
# intentionally overridable from the command line (--tier) so the detector
# is not welded to one roster.
DEFAULT_TIERS: Dict[str, int] = {
    "haiku": 1,
    "sonnet": 2,
    "opus": 3,
    "fable": 4,
}

# Severities
VIOLATION = "VIOLATION"
WARNING = "WARNING"
INFO = "INFO"


def normalise_model(name: Optional[str]) -> Optional[str]:
    """Map a concrete model id to a tier key.

    Accepts marketing ids like 'claude-opus-4-8' or 'gpt-5.6-sol' and
    reduces them to a coarse tier key when possible. Unknown ids are
    returned lower-cased so an explicit --tier entry can cover them.
    """
    if name is None:
        return None
    n = name.strip().lower()
    if not n:
        return None
    for key in ("fable", "opus", "sonnet", "haiku"):
        if key in n:
            return key
    return n


@dataclass
class Finding:
    session_id: str
    check: str          # "a" | "b" | "c"
    code: str           # machine code, e.g. V_B_TIER_INVERSION
    severity: str
    message: str
    spawn_id: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "check": self.check,
            "code": self.code,
            "severity": self.severity,
            "spawn_id": self.spawn_id,
            "message": self.message,
        }


@dataclass
class SessionResult:
    session_id: str
    case: Optional[str]
    parent_model: Optional[str]
    rule_delivery: Optional[str]
    context_state: Optional[str]
    spawn_count: int
    findings: List[Finding] = field(default_factory=list)
    # per-check verdicts for the report's 切り分け表
    check_a: str = "n/a"
    check_b: str = "n/a"
    check_c: str = "n/a"

    @property
    def violations(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == VIOLATION]


def _load_events(path: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}")
    return events


def _verdict(findings: List[Finding], check: str, applicable: bool) -> str:
    if not applicable:
        return "n/a"
    for f in findings:
        if f.check == check and f.severity == VIOLATION:
            return "FAIL"
    for f in findings:
        if f.check == check and f.severity == WARNING:
            return "WARN"
    return "PASS"


def analyse_session(
    session_id: str,
    events: List[Dict[str, Any]],
    tiers: Dict[str, int],
) -> SessionResult:
    """Reconstruct (a)/(b)/(c) compliance from raw structural events."""
    events = sorted(events, key=lambda e: e.get("seq", 0))
    meta = next((e for e in events if e.get("type") == "session_meta"), {})
    parent_model = normalise_model(meta.get("parent_model"))
    parent_tier = tiers.get(parent_model) if parent_model else None
    min_tier = min(tiers.values()) if tiers else 1

    model_tables = [e for e in events if e.get("type") == "model_table"]
    spawns = [e for e in events if e.get("type") == "agent_spawn"]
    reviews = [e for e in events if e.get("type") == "review"]

    result = SessionResult(
        session_id=session_id,
        case=meta.get("case"),
        parent_model=parent_model,
        rule_delivery=meta.get("rule_delivery"),
        context_state=meta.get("context_state"),
        spawn_count=len(spawns),
    )
    findings = result.findings

    first_spawn_seq = min((s.get("seq", 0) for s in spawns), default=None)

    # --- Check (a): model-table declaration before spawning ---------------
    if spawns:
        if not model_tables:
            findings.append(Finding(
                session_id, "a", "V_A_NO_MODEL_TABLE", VIOLATION,
                "no model-table declaration found before any spawn",
            ))
        else:
            earliest_table = min(t.get("seq", 0) for t in model_tables)
            if first_spawn_seq is not None and earliest_table > first_spawn_seq:
                findings.append(Finding(
                    session_id, "a", "V_A_TABLE_LATE", VIOLATION,
                    "model table declared only after spawning began",
                ))
            declared: Dict[str, str] = {}
            for t in model_tables:
                declared.update(t.get("declares", {}) or {})
            for s in spawns:
                st = s.get("subagent_type")
                if st is not None and st not in declared:
                    findings.append(Finding(
                        session_id, "a", "V_A_TABLE_INCOMPLETE", VIOLATION,
                        f"spawn '{st}' not covered by the declared model table",
                        spawn_id=s.get("spawn_id"),
                    ))

    # --- Check (b): explicit model + tier <= parent (格下原則) -------------
    reviews_by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for r in reviews:
        reviews_by_ref.setdefault(r.get("spawn_ref"), []).append(r)

    for s in spawns:
        spawn_id = s.get("spawn_id")
        sub_model = normalise_model(s.get("model"))
        if sub_model is None:
            findings.append(Finding(
                session_id, "b", "V_B_MODEL_MISSING", VIOLATION,
                "subagent spawned without an explicit model",
                spawn_id=spawn_id,
            ))
        else:
            sub_tier = tiers.get(sub_model)
            if sub_tier is None:
                findings.append(Finding(
                    session_id, "b", "V_B_UNKNOWN_MODEL", WARNING,
                    f"model '{sub_model}' not in tier map; tier undecidable",
                    spawn_id=spawn_id,
                ))
            elif parent_tier is None:
                findings.append(Finding(
                    session_id, "b", "V_B_UNKNOWN_PARENT", WARNING,
                    "parent model/tier unknown; tier relation undecidable",
                    spawn_id=spawn_id,
                ))
            else:
                exception = s.get("exception")
                escalation = bool(s.get("escalation_declared"))
                if sub_tier > parent_tier:
                    if escalation:
                        findings.append(Finding(
                            session_id, "b", "I_B_ESCALATION", INFO,
                            "higher-tier subagent declared as escalation signal",
                            spawn_id=spawn_id,
                        ))
                    else:
                        findings.append(Finding(
                            session_id, "b", "V_B_TIER_INVERSION", VIOLATION,
                            f"subagent tier ({sub_model}) higher than parent "
                            f"({parent_model}) without escalation -- command "
                            f"structure inversion",
                            spawn_id=spawn_id,
                        ))
                elif sub_tier == parent_tier:
                    at_cheapest = parent_tier == min_tier
                    if exception == "a" or at_cheapest:
                        findings.append(Finding(
                            session_id, "b", "I_B_SAMETIER_OK", INFO,
                            "same-tier spawn under exception (a) / cheapest tier",
                            spawn_id=spawn_id,
                        ))
                    else:
                        findings.append(Finding(
                            session_id, "b", "W_B_SAME_TIER", WARNING,
                            "same-tier spawn without exception (a); default is "
                            "one tier down",
                            spawn_id=spawn_id,
                        ))
                # sub_tier < parent_tier -> satisfies default, no finding

    # --- Check (c): evidence-cited review of each spawn -------------------
    for s in spawns:
        spawn_id = s.get("spawn_id")
        revs = reviews_by_ref.get(spawn_id, [])
        cited = any((r.get("citations") or []) for r in revs)
        if not cited:
            findings.append(Finding(
                session_id, "c", "V_C_NO_EVIDENCE_REVIEW", VIOLATION,
                "no review with cited evidence references this spawn",
                spawn_id=spawn_id,
            ))

    applicable = bool(spawns)
    result.check_a = _verdict(findings, "a", applicable)
    result.check_b = _verdict(findings, "b", applicable)
    result.check_c = _verdict(findings, "c", applicable)
    return result


def analyse_log(path: str, tiers: Dict[str, int]) -> List[SessionResult]:
    events = _load_events(path)
    by_session: Dict[str, List[Dict[str, Any]]] = {}
    for e in events:
        by_session.setdefault(e.get("session_id", "unknown"), []).append(e)
    return [analyse_session(sid, evs, tiers) for sid, evs in by_session.items()]


def _parse_tier_overrides(raw: List[str]) -> Dict[str, int]:
    tiers = dict(DEFAULT_TIERS)
    for item in raw:
        if "=" not in item:
            raise SystemExit(f"--tier expects key=int, got: {item!r}")
        key, val = item.split("=", 1)
        tiers[key.strip().lower()] = int(val)
    return tiers


def _print_human(results: Iterable[SessionResult]) -> None:
    for r in results:
        header = f"session {r.session_id}"
        if r.case:
            header += f" (case {r.case})"
        print(f"\n=== {header} ===")
        print(f"  parent_model : {r.parent_model}")
        print(f"  rule_delivery: {r.rule_delivery}   context: {r.context_state}")
        print(f"  spawns       : {r.spawn_count}")
        print(f"  (a) model-table : {r.check_a}")
        print(f"  (b) model/tier  : {r.check_b}")
        print(f"  (c) evidence    : {r.check_c}")
        if not r.findings:
            print("  findings     : none")
        for f in r.findings:
            loc = f" [{f.spawn_id}]" if f.spawn_id else ""
            print(f"  - {f.severity:9s} ({f.check}) {f.code}{loc}: {f.message}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("logs", nargs="+", help="session-log .jsonl file(s)")
    ap.add_argument("--tier", action="append", default=[],
                    metavar="KEY=INT", help="override/add a model tier")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON instead of a table")
    args = ap.parse_args(argv)

    tiers = _parse_tier_overrides(args.tier)
    all_results: List[SessionResult] = []
    for path in args.logs:
        all_results.extend(analyse_log(path, tiers))

    total_violations = sum(len(r.violations) for r in all_results)

    if args.json:
        payload = {
            "tier_map": tiers,
            "total_violations": total_violations,
            "sessions": [
                {
                    "session_id": r.session_id,
                    "case": r.case,
                    "parent_model": r.parent_model,
                    "rule_delivery": r.rule_delivery,
                    "context_state": r.context_state,
                    "spawns": r.spawn_count,
                    "check_a": r.check_a,
                    "check_b": r.check_b,
                    "check_c": r.check_c,
                    "findings": [f.as_dict() for f in r.findings],
                }
                for r in all_results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(all_results)
        print(f"\nTOTAL VIOLATIONS: {total_violations} "
              f"across {len(all_results)} session(s)")

    # Non-zero exit iff at least one VIOLATION fired (warnings do not fail).
    return 1 if total_violations else 0


if __name__ == "__main__":
    sys.exit(main())
