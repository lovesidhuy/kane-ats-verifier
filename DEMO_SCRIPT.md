# 3-minute demo script (Nov 2026)

Map each beat to judging criteria. Commands assume repo root after `git clone`.

| Time | Criterion | Show | Say |
|------|-----------|------|-----|
| 0:00–0:30 | **Ships** | `README.md` → `README_KANE_HACKATHON.md` | Standalone `ats_verifier/` + Kane CLI as grader; harness dry-run + network guard prevent real submits. |
| 0:30–1:00 | **Verified** | `./scripts/run_kane_verify.sh doctor` then `demo` | 29 pytest + replay; numbers from `check_claims` / **54** suites, **37** packs, **190** trajectories (**50** sample). |
| 1:00–2:00 | **Closed loop** | `evidence/loop_runs/cl2_visa_seed_live/summary.json`, `KANE_CAUGHT.md` | CL-2: attempt 1 **failed** on visa seed, agent writes `policy_override` to `.loop_agent_policy.json`, attempt 2 **passed** with seed still active (~39.6 cr). |
| 2:00–2:30 | **Craft** | `evidence/verified_trajectories_sample_50.jsonl`, `scripts/kane_loop.py` | Reward-filtered trajectories; replay is 0 credits; sealed packs are L1 evidence. |
| 2:30–3:00 | **Safety** | `tests/kane/36_network_no_submit_guard_test.md`, `evidence/loop_runs/p0_3_suite36_pass/` | External submit blocked; P0-3 live pass recorded. |

## Terminal block (recording)

```bash
./scripts/run_kane_verify.sh doctor
./scripts/run_kane_verify.sh demo
python3 scripts/check_claims.py
```

## Files to have open

- `evidence/evidence_index.json` (suite statuses incl. suite 53 **failed** before fix)
- `evidence/SUITE_53_KANE_TRIAGE.md` (K-16)
- `evidence/loop_runs/cl2_visa_seed_live/attempt_1/kane.ndjson` (failure excerpts)

## 60-second pitch

> Our autofill agent fills complex ATS forms; **Kane CLI** verifies every run before submit. Judges replay the closed loop in **0 credits** with `./scripts/run_kane_verify.sh demo`. We ship **54** indexed suites, **37** sealed packs, **22** loop runs, and **190** verified trajectories — and we keep failed evidence when Kane catches bugs like the dedupe POST 415 (K-16).
