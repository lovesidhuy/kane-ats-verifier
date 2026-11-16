# Judges quickstart

## Replay (no LambdaTest login, 0 credits)

```bash
git clone https://github.com/lovesidhuy/kane-ats-verifier.git
cd kane-ats-verifier
python3 -m pip install -r requirements.txt
./scripts/run_kane_verify.sh doctor
./scripts/run_kane_verify.sh demo
```

Artifacts: `evidence/loop_runs/judge_demo/summary.json` (replay red→fix→green on NDJSON fixtures).

**Cold-clone timing:** `demo` ~1.5s wall (29 pytest + replay + claims), `check_claims` ~0.5s.

| Metric | Source |
|--------|--------|
| **54** suites indexed | `SUBMISSION.json` |
| **29** standalone pytest tests | `demo` output |
| **41** sealed packs | `evidence_index.json` |
| **22** loop runs recorded | `evidence/loop_runs/` |
| **190** trajectories (**50** public sample) | `evidence/dataset_manifest.json` |
| Credits **1119.31** Σ / **1742.05** Δ | `credits_ledger.csv` |

## Live closed loop (optional)

Requires `npm i -g @testmuai/kane-cli` and:

```bash
export LT_USERNAME=...
export LT_ACCESS_KEY=...
kane-cli login --username "$LT_USERNAME" --access-key "$LT_ACCESS_KEY"
```

Then:

```bash
./scripts/run_kane_verify.sh loop --live \
  --seed-bug visa_wrong_answer \
  --suite tests/kane/17_persona_visa_ashby_strict_test.md \
  --max-attempts 2 --credit-budget 60 \
  --save-evidence --run-id cl2_visa_seed_live
```

Recorded artifact already in repo: `evidence/loop_runs/cl2_visa_seed_live/` (~40 credits, Nov 14 2026).

## If Kane auth fails

Use replay only (`demo`). Pass/fail is in `test_md_done.overall_status` inside `attempt_*/kane.ndjson`.

## Safety

- Harness only (`127.0.0.1:8766`) for loop/mutation; network guard blocks external POST.
- No real employer submits; `SAFETY_GUARD_ACTIVE` is UI dry-run only plus network guard.

## FAQ

| Question | Answer |
|----------|--------|
| Where is the engine? | Clean standalone `ats_verifier/` + `tests/kane/harness.py` + `scripts/kane_loop.py` |
| CAPTCHA/proxies? | **Out of scope / not included** — see `HACKATHON_SCOPE.md` |
| Validate evidence zip? | Integrity only; use `overall_status` for pass/fail |
| Claims table | `README_KANE_HACKATHON.md` + `python3 scripts/check_claims.py` |
