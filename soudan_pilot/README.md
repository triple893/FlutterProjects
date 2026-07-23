# soudan_pilot — subagent-tier discipline detector + pilot (DIRECTION 20260723a D2)

Mechanical detector for the "サブagent格下原則" (L-034 / DIRECTIVE補則2):
given a session log, it reconstructs — with **no self-reported PASS field**
— whether the parent, for each subagent spawn:

- **(a)** declared a model table before spawning,
- **(b)** made the model explicit and kept the subagent tier ≤ parent
  (default one tier down; a higher-tier spawn is a violation unless
  declared as an escalation),
- **(c)** reviewed the output with cited evidence.

## Run

```bash
cd soudan_pilot
python3 -m unittest test_detector -v        # 9 unit tests
python3 run_pilot.py                         # 切り分け表 + firing self-check
python3 detect_tier_violations.py fixtures/C3_link_only_elapsed.jsonl  # exits 1
```

## On real Claude Code logs

```bash
python3 transcript_adapter.py ~/.claude/projects/<proj>/<session>.jsonl live \
  | python3 detect_tier_violations.py /dev/stdin
```

The adapter reads spawns from `Task`/`Agent` `tool_use` blocks (a missing
`model` is exactly the (b) violation the detector catches). It expects two
explicit, auditable markers in the parent's text for (a)/(c):

```
<!-- MODEL_TABLE {"Explore":"haiku","general-purpose":"sonnet"} -->
<!-- REVIEW spawn=s1 cite="file:foo.py:10; result: 3 refs" -->
```

Their **absence** is what the detector flags — so the markers are
structural evidence, never a self-graded verdict.

## Files

- `detect_tier_violations.py` — the detector (stdlib only, CI-gate exit code)
- `transcript_adapter.py` — real-transcript → canonical-event adapter
- `run_pilot.py` — runs all fixtures, prints triage table + firing self-check
- `test_detector.py` — unit tests (compliant path + every violation code)
- `fixtures/C1..C3*.jsonl` — pilot-case validation fixtures
- `pilot_run.log` — captured run evidence
- `REPORT_20260723_soudan_pilot.md` — factual report (scope, results, limits)

## Scope / honesty

Fixtures are hand-authored to **validate the detector**; they are not a
behavioural measurement of live sessions. See the REPORT §4 for the limit
and §5 for why nothing is routed to L-031 (D3) from this run.
