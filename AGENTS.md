# AI Agents & Kane CLI Workflow

This repository is a clean, standalone **ATS Application Verification & Closed-Loop Self-Healing** artifact built and verified end-to-end with **TestMu AI Kane CLI** (`@testmuai/kane-cli` v0.10.4) during the KaneCLI Online Hackathon (Nov 12–19, 2026).

> **One-Liner:** *"An agent that fills job applications on any ATS, and Kane makes sure it never submits a broken one — turning every green run into verified training data for browser agents."*

## Architecture

1. **Standalone Verification Engine (`ats_verifier/`)**
   - `ats_verifier/dom_autofill.py` (`DOMAutofillEngine`, `SCAN_FIELDS_JS`, `INJECT_VALUES_JS`)
   - `ats_verifier/form_answers.py` (`load_profile`, `resolve_answer`, `ResolvedAnswer`)
   - `ats_verifier/discovery.py` (`RawJob`, `normalize_raw_job`, `deduplicate`, `classify_apply_type`)
2. **Two-Tier Non-Invasive Verification (`tests/kane/harness.py` + Live Public ATS)**
   - **Tier 1 (Live Public No-Login ATS in Dry-Run):** Verified against active public postings on `job-boards.greenhouse.io` (`11_live_greenhouse_test.md`) and `jobs.lever.co` (`12_live_lever_test.md`), halting before final submit.
   - **Tier 2 (Multi-Persona & Adversarial DOM/Policy Harness on `PORT=8766`):** Standalone Flask harness supporting **10 synthetic candidate personas**, **7 ATS/portal layouts** (`Greenhouse`, `Lever`, `Ashby`, `BambooHR`, `Indeed SmartApply`, `LinkedIn Easy Apply`, `Workopolis / Job Bank Canada`), and **4 adversarial variants** (`standard`, `mutated_ids`, `strict_policy_screening`, `dirty_dedup_batch`), plus `/tools/qa-bank`, `/tools/discovery-dedupe`, and `/tools/network-guard-test`.
3. **Closed-Loop Kane CLI Authoring, Triage & Self-Healing (`scripts/kane_loop.py`)**
   - Parses Kane NDJSON (`test_md_done.overall_status`) + packed `failure.yaml` into a structured `FixPlan` (`harness_patch`, `policy_override`, `set_value`, etc.).
   - Writes overrides in canonical `.loop_agent_policy.json` format (`{"source": "...", "fields": {...}}`) while planted seeds stay active, and retries automatically under `--credit-budget`.
   - Indexed **54** `.testmd` suites, **23** sealed `.evidence` packs (`kane-cli evidence validate` L1 finalized), **18** loop runs, and **162** reward-filtered JSONL trajectories (**50** public sample).
