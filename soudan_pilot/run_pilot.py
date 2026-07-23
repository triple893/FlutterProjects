#!/usr/bin/env python3
"""Run the tier-violation detector over the C1/C2/C3 pilot fixtures and
print the 切り分け表 (triage table) plus a detection-firing self-check.

The self-check encodes DIRECTION 20260723a D2's explicit requirement:
"正常系だけで完了扱いにせず、違反ケースで検出が実際に発火することを物理観測".
It is NOT enough that the compliant case passes; the detector must
actually FIRE on the cases that carry violations. This runner asserts
that contract and exits non-zero if it is broken.
"""

from __future__ import annotations

import glob
import os
import sys

from detect_tier_violations import DEFAULT_TIERS, analyse_log

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = sorted(glob.glob(os.path.join(HERE, "fixtures", "*.jsonl")))

# Contract: which cases MUST be clean and which MUST trip the detector.
EXPECT_CLEAN = {"C1"}
EXPECT_FIRES = {"C2", "C3"}


def main() -> int:
    results = []
    for path in FIXTURES:
        results.extend(analyse_log(path, DEFAULT_TIERS))
    results.sort(key=lambda r: r.session_id)

    print("切り分け表 (triage table) -- reconstructed mechanically, "
          "no self-report\n")
    hdr = f"{'case':6} {'delivery':16} {'ctx':6} {'(a)':6} {'(b)':6} {'(c)':6} {'viol':4}"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        print(f"{str(r.case or r.session_id):6} "
              f"{str(r.rule_delivery or '-'):16} "
              f"{str(r.context_state or '-'):6} "
              f"{r.check_a:6} {r.check_b:6} {r.check_c:6} "
              f"{len(r.violations):<4}")

    print("\nfindings detail:")
    for r in results:
        for f in r.findings:
            loc = f" [{f.spawn_id}]" if f.spawn_id else ""
            print(f"  {r.session_id}: {f.severity:9s} ({f.check}) "
                  f"{f.code}{loc}: {f.message}")

    # --- detection-firing self-check -------------------------------------
    print("\ndetection-firing self-check:")
    ok = True
    by_case = {(r.case or r.session_id): r for r in results}
    for case in sorted(EXPECT_CLEAN | EXPECT_FIRES):
        r = by_case.get(case)
        if r is None:
            print(f"  {case}: MISSING fixture -> FAIL")
            ok = False
            continue
        n = len(r.violations)
        if case in EXPECT_CLEAN:
            passed = n == 0
            print(f"  {case}: expected 0 violations, observed {n} -> "
                  f"{'OK' if passed else 'FAIL'}")
        else:
            passed = n > 0
            print(f"  {case}: expected detector to FIRE, observed {n} "
                  f"violation(s) -> {'OK (fired)' if passed else 'FAIL (silent)'}")
        ok = ok and passed

    print(f"\nself-check: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
