# Verification Scope & Safety Safeguards

This repository is a standalone **closed-loop browser verification system** for job application autofill agents.

## Supported Capabilities

- `ats_verifier/` — standalone DOM autofill, deterministic QA policy resolver, and discovery deduplicator
- `tests/kane/harness.py` — local ATS matrix (7 ATS × 10 personas × 4 variants), dry-run only, network submit guard
- `scripts/kane_loop.py` — closed loop + `.loop_agent_policy.json` overrides + replay
- `scripts/run_kane_verify.sh` and `./kane-ats` — unified CLI, `demo`, `doctor`, `loop`
- `evidence/` — 45 sealed `.evidence` packs, 23 loop runs, 50-row trajectory sample, CL-2 showcase
- Technical docs: `SPECIFICATION.md`, `KANE_CAUGHT.md`, `VERIFICATION.md`, `DATASET_CARD.md`, `ARCHITECTURE.md`

## Explicitly Excluded

- CAPTCHA solving
- Proxy ladders / residential proxies
- Anti-detect browsers or stealth plugins
- Real-employer form submission (all verification runs against `http://127.0.0.1:8766` or dry-run boards without final submit)
