#!/usr/bin/env python3
"""Run the SOUDAN gate detector over the pilot fixtures and assert the
detection-firing contract (意思決定支援室 §6 minimal pilot).

Requirement: not enough that the compliant package passes -- each gate
must actually FIRE on the fixture built to violate it (completeness,
conflict-of-interest, authority-citation). Exits non-zero if the contract
is broken.
"""

from __future__ import annotations

import os
import sys

from detect_soudan_gate import check_soudan, check_citation

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "soudan_fixtures")


def _read(name):
    with open(os.path.join(FX, name), encoding="utf-8") as fh:
        return fh.read()


def main() -> int:
    cases = [
        # (label, result, expect_fire, gate-of-interest note)
        ("S1_complete_ok",
         check_soudan("S1", _read("S1_complete_ok.md")), False, "clean"),
        ("S2_incomplete",
         check_soudan("S2", _read("S2_incomplete.md")), True, "completeness"),
        ("S3_coi_kuro",
         check_soudan("S3", _read("S3_coi_kuro.md")), True, "conflict-of-interest"),
        ("citing_related_ok",
         check_citation("rel", _read("citing_related_ok.md")), False, "clean"),
        ("citing_authority_bad",
         check_citation("auth", _read("citing_authority_bad.md")), True, "authority"),
    ]

    print("SOUDAN gate pilot -- findings\n")
    for label, res, _, _ in cases:
        print(f"[{label}]")
        if not res.findings:
            print("  none (all gates pass)")
        for f in res.findings:
            print(f"  - {f.line()}")
        print()

    print("detection-firing self-check:")
    ok = True
    for label, res, expect_fire, note in cases:
        n = len(res.violations)
        if expect_fire:
            passed = n > 0
            print(f"  {label}: expect FIRE ({note}) -> {n} violation(s) -> "
                  f"{'OK (fired)' if passed else 'FAIL (silent)'}")
        else:
            passed = n == 0
            print(f"  {label}: expect CLEAN -> {n} violation(s) -> "
                  f"{'OK' if passed else 'FAIL'}")
        ok = ok and passed

    print(f"\nself-check: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
