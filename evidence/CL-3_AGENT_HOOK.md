# CL-3 — Kane hook in the agent self-healing loop (execution trace)

**Hook:** after each `kane-cli testmd run`, parse NDJSON (`test_md_done`, assertion events) → `build_fixplan()` → write agent policy (`tests/kane/.loop_agent_policy.json`) → retry.

## Red (attempt 1, live)

```
Kane: test_md_done overall_status=failed
Assertion: select id "sponsorship" has value "Yes" → passed=false (actual No)
Diagnosis: visa_wrong_answer (expected Yes, got No)
```

## Fix (agent, not harness admin)

```
FixPlan: policy_override target=sponsorship value=Yes
Action: agent_policy_override_applied
File: tests/kane/.loop_agent_policy.json {"fields":{"sponsorship":"Yes"}}
Seed file tests/kane/.loop_seed_bug unchanged (still visa_wrong_answer)
```

## Green (attempt 2, live)

```
Kane: test_md_done overall_status=passed
seed_bug_active: visa_wrong_answer
agent_policy: {"sponsorship": "Yes"}
Credits (balance delta): ~39.6
Evidence: evidence/loop_runs/cl2_visa_seed_live/
```

Full NDJSON: `attempt_1/kane.ndjson`, `attempt_2/kane.ndjson`.