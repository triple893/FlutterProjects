#!/usr/bin/env python3
"""Unit tests for detect_soudan_gate. Exercises the compliant path and each
gate's violation. Run: python -m unittest test_soudan_gate -v
"""

import unittest

from detect_soudan_gate import (
    check_soudan, check_citation, split_frontmatter, normalise_person,
    VIOLATION,
)

COMPLETE = """---
authority: none
read_policy: never_first
soudan_id: S-20260723-99
subject: 案件X
prepared_by: codex
committed_by: codex
for_decider: kuro
---
## 1. 論点
x
## 2. 意図
x
## 3. 材料
x
## 4. 選択肢
- 案A
- 案B
## 5. 推奨案
x
## 6. 指示案
x
## 7. チェックリスト
x
## 8. 危険
x
"""


def vcodes(res):
    return {f.code for f in res.findings if f.severity == VIOLATION}


class TestSoudanGate(unittest.TestCase):
    def test_frontmatter_strips_inline_comment(self):
        fm, _ = split_frontmatter(COMPLETE)
        self.assertEqual(fm["authority"], "none")
        self.assertEqual(fm["subject"], "案件X")

    def test_normalise_person_aliases(self):
        self.assertEqual(normalise_person("claude"), "kuro")
        self.assertEqual(normalise_person("Codex"), "codex")
        self.assertEqual(normalise_person("gemini"), "gura")
        self.assertEqual(normalise_person("丼ちゃん"), "丼ちゃん")
        self.assertIsNone(normalise_person("案件X"))

    def test_complete_is_clean(self):
        res = check_soudan("c", COMPLETE)
        self.assertEqual(vcodes(res), set())

    def test_missing_section_fires(self):
        text = COMPLETE.replace("## 6. 指示案\nx\n", "")
        res = check_soudan("c", text)
        self.assertIn("V_B_SECTION_MISSING", vcodes(res))

    def test_too_few_options_fires(self):
        text = COMPLETE.replace("- 案A\n- 案B\n", "- 案A\n")
        res = check_soudan("c", text)
        self.assertIn("V_B_TOO_FEW_OPTIONS", vcodes(res))

    def test_conflict_of_interest_fires(self):
        text = COMPLETE.replace("subject: 案件X", "subject: kuro")
        res = check_soudan("c", text)
        self.assertIn("V_C_CONFLICT_OF_INTEREST", vcodes(res))
        # subject=kuro with for_decider=kuro AND prepared/committed=codex ->
        # only for_decider trips (prepared/committed are codex != kuro)
        coi = [f for f in res.findings if f.code == "V_C_CONFLICT_OF_INTEREST"]
        self.assertTrue(any("for_decider" in f.message for f in coi))

    def test_coi_na_when_subject_not_person(self):
        res = check_soudan("c", COMPLETE)  # subject 案件X
        self.assertNotIn("V_C_CONFLICT_OF_INTEREST", vcodes(res))

    def test_authority_not_none_fires(self):
        text = COMPLETE.replace("authority: none", "authority: DISPATCH_LEDGER")
        res = check_soudan("c", text)
        self.assertIn("V_D_AUTHORITY_NOT_NONE", vcodes(res))

    def test_bad_decider_fires(self):
        text = COMPLETE.replace("for_decider: kuro", "for_decider: codex")
        res = check_soudan("c", text)
        self.assertIn("V_A_BAD_DECIDER", vcodes(res))

    def test_citation_related_is_clean(self):
        text = ("---\nauthority: L-038\nrelated: S-20260723-01\n---\n"
                "本文は L-038 が根拠。\n")
        res = check_citation("m", text)
        self.assertEqual(vcodes(res), set())

    def test_citation_authority_field_fires(self):
        text = "---\nauthority: S-20260723-01\nrelated: L-038\n---\nbody\n"
        res = check_citation("m", text)
        self.assertIn("V_D_SOUDAN_AS_AUTHORITY", vcodes(res))

    def test_citation_konkyo_body_fires(self):
        text = ("---\nauthority: L-038\nrelated: L-038\n---\n"
                "## 根拠\n相談 S-20260723-01 を根拠に実行する。\n")
        res = check_citation("m", text)
        self.assertIn("V_D_SOUDAN_AS_BASIS", vcodes(res))


if __name__ == "__main__":
    unittest.main(verbosity=2)
