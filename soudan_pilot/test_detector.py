#!/usr/bin/env python3
"""Unit tests for detect_tier_violations.

Covers the compliant path AND every violation code, so the abnormal cases
are exercised rather than only the happy path (L-038/L-040 discipline).
Run: python -m unittest test_detector -v
"""

import unittest

from detect_tier_violations import DEFAULT_TIERS, analyse_session, VIOLATION


def codes(result):
    return {f.code for f in result.findings}


def viol_codes(result):
    return {f.code for f in result.findings if f.severity == VIOLATION}


class TestDetector(unittest.TestCase):
    def _run(self, events):
        return analyse_session("T", events, DEFAULT_TIERS)

    def test_compliant_one_tier_down(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"Explore": "haiku"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "Explore", "model": "haiku"},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["evidence"]},
        ]
        r = self._run(events)
        self.assertEqual(r.violations, [])
        self.assertEqual((r.check_a, r.check_b, r.check_c),
                         ("PASS", "PASS", "PASS"))

    def test_missing_model_table(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "agent_spawn", "session_id": "T", "seq": 1,
             "spawn_id": "s1", "subagent_type": "Explore", "model": "haiku"},
            {"type": "review", "session_id": "T", "seq": 2,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertIn("V_A_NO_MODEL_TABLE", viol_codes(r))
        self.assertEqual(r.check_a, "FAIL")

    def test_model_missing(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"Explore": "haiku"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "Explore", "model": None},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertIn("V_B_MODEL_MISSING", viol_codes(r))

    def test_tier_inversion_without_escalation(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"g": "fable"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "g", "model": "fable",
             "escalation_declared": False},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertIn("V_B_TIER_INVERSION", viol_codes(r))

    def test_tier_inversion_declared_as_escalation_is_info(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"g": "fable"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "g", "model": "fable",
             "escalation_declared": True},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertNotIn("V_B_TIER_INVERSION", viol_codes(r))
        self.assertIn("I_B_ESCALATION", codes(r))

    def test_same_tier_warns_without_exception(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"g": "opus"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "g", "model": "opus"},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertIn("W_B_SAME_TIER", codes(r))
        self.assertEqual(viol_codes(r), set())  # warning only, not a violation
        self.assertEqual(r.check_b, "WARN")

    def test_same_tier_ok_under_exception_a(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"g": "opus"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "g", "model": "opus",
             "exception": "a"},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": ["e"]},
        ]
        r = self._run(events)
        self.assertNotIn("W_B_SAME_TIER", codes(r))
        self.assertEqual(r.check_b, "PASS")

    def test_no_evidence_review(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"Explore": "haiku"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "Explore", "model": "haiku"},
        ]
        r = self._run(events)
        self.assertIn("V_C_NO_EVIDENCE_REVIEW", viol_codes(r))

    def test_empty_citations_is_not_a_review(self):
        events = [
            {"type": "session_meta", "session_id": "T", "seq": 0,
             "parent_model": "opus"},
            {"type": "model_table", "session_id": "T", "seq": 1,
             "declares": {"Explore": "haiku"}},
            {"type": "agent_spawn", "session_id": "T", "seq": 2,
             "spawn_id": "s1", "subagent_type": "Explore", "model": "haiku"},
            {"type": "review", "session_id": "T", "seq": 3,
             "spawn_ref": "s1", "citations": []},
        ]
        r = self._run(events)
        self.assertIn("V_C_NO_EVIDENCE_REVIEW", viol_codes(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)
