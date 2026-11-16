# Kane caught it — closed-loop bugs (V-1 / V-2)

Pass/fail is from `test_md_done.overall_status` / pack `result.yaml`, not `evidence validate` alone.

| ID | Bug | Kane signal | Failed run | Fixed run | Regression |
|----|-----|-------------|------------|-----------|------------|
| K-01 | Email mismatch vs profile in suite 01 | assertion on email | fixtures / live greenhouse early run | spec aligned to `load_profile()` | `01_greenhouse_autofill_test.md` |
| K-02 | `answers[key]` list-index TypeError on strict/mutated personas | HTTP 500 `/api/resolve-fields` | `tests/fixtures/ndjson/red.ndjson` | harness `_set_answer()` patch | `14_policy_guardrails_test.md`, `26_mutated_dom_bamboohr_test.md` |
| K-03 | QA bank years vs policy (suite 24) | wrong `years` value | red in QA bank step | test aligned to `form_answers.py` | `24_qa_bank_python_exp_test.md` |
| K-04 | Visa sponsorship `No` for visa persona (CL-2 planted) | sponsorship assert | `evidence/loop_runs/cl2_visa_seed_live/attempt_1` | agent `policy_override` + attempt 2 | `17_persona_visa_ashby_strict_test.md` + loop |
| K-05 | First name strict persona | field value | harness strict variant | persona matrix | `17_*`, `19_*` |
| K-06 | Mutated DOM ids break inject | AUTOFILL incomplete | mutated suites pre-fix | `mutated_ids` field map | `13_mutated_dom_resilience_test.md` |
| K-07 | Policy clearance question | clearance select | strict_policy runs | persona clearance map | `14_policy_guardrails_test.md` |
| K-08 | Salary expectation strict | salary assert | strict ashby | persona salary | `17_persona_visa_ashby_strict_test.md` |
| K-09 | Work auth mismatch | select value | policy suites | persona work_auth | `14_policy_guardrails_test.md` |
| K-10 | Harness connection refused | broken / unreachable | live flake logs | `ensure_local_harness()` | loop unit tests |
| K-11 | Kane lock denied | auth 403 | env | classify env not agent | `kane_loop` lock detection |
| K-12 | External submit attempt (safety) | would reach employer | without network guard | P0-3 fetch/XHR block | `36_network_no_submit_guard_test.md` |
| K-13 | Dirty dedup batch noise | dedup count | optional batch 36→48 | dedupe tool | `48_dirty_dedup_batch_test.md` |
| K-14 | Explore lease without assertions | 0 pass/fail checks | explore summary | mutation unit tests | `tests/test_mutation_check.py` |
| K-15 | Agent repeated same fixplan | stopped repeated | loop before agent override | agent policy file | CL-2 honest rerun |
| **K-16** | **Dedupe POST 415** (`runDedupe` no Content-Type) | `test_md_done` **failed** (live) | `v1_explore_53_live`, `v1_explore_53_live_b` NDJSON | **fixed & verified passed live** (`53_explore_discovery_dedupe_passed.evidence`) | `53_explore_discovery_dedupe_test.md`, `tests/test_discovery_dedupe_api.py` |

## Live re-recordings (Sprint 2)

| Run ID | Suite | `test_md_done` | Credits (balance Δ) |
|--------|-------|----------------|---------------------|
| `p0_3_suite36_pass` | `36_network_no_submit_guard_test.md` | **passed** | ~45.9 |
| `p0_3_suite36_broken_fail` | `36_network_no_submit_guard_broken_test.md` | **failed** (expected) | ~22.4 |
| `cl4_email_seed_live` | `01_greenhouse_autofill_test.md` + `email_wrong_answer` | att1 **failed** / att2 **passed** | ~78.9 |
| `cl4_salary_seed_live` | `17_*` + `salary_wrong_answer` | att1 **failed** / att2 **passed** | ~42.5 |
| `v1_explore_50_live` | `50_explore_harness_home_test.md` | **passed** | ~32.4 |
| `v1_explore_51_live` | `51_explore_ashby_smoke_test.md` | **passed** | ~38.7 |
| `v1_explore_52_live` | `52_explore_qa_bank_test.md` | **passed** | ~32.8 |
| `v1_explore_53_live` | `53_explore_discovery_dedupe_test.md` | **failed** (spec tightened) | ~42.1 |
| `v1_explore_54_live` | `54_explore_lever_smoke_test.md` | **passed** | ~32.8 |
| `cl2_visa_seed_live_v2` | `17_*` + `visa_wrong_answer` | att1 **failed** / att2 **passed** | ~38.2 |
| `cl4_salary_seed_live_v2` | `17_*` + `salary_wrong_answer` | att1 **failed** / att2 **passed** | ~34.4 |
| `cl4_email_seed_live_v2` | `01_*` + `email_wrong_answer` | att1 **failed** / att2 **passed** | ~90.4 |
| `53_explore_discovery_dedupe` | `53_explore_discovery_dedupe_test.md` | **passed** (K-16 confirmed) | ~14.7 |
| `48_dirty_dedup_batch` | `48_dirty_dedup_batch_test.md` | **passed** (dirty dedupe) | ~15.0 |

**V-3 mutations (fail → revert → pass):** guard-off **failed** `p0_3_suite36_broken_fail`; guard-on **passed** `p0_3_suite36_pass`; planted seed loops **failed** then agent policy **passed** (`cl2_visa_seed_live`, `cl4_email_seed_live`, `cl4_salary_seed_live`, `cl2_visa_seed_live_v2`, `cl4_salary_seed_live_v2`, `cl4_email_seed_live_v2`).

**Explore note:** Four explore campaigns (`exploration_id` in `AGENTS.md`) committed **141** lease deltas; `50`–`54` regressions are live Kane smokes on harness frontiers discovered during explore.