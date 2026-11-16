# Kane CLI Online Hackathon — Ready-to-Submit Form Copy

Submit at: `https://www.kaneclihack.sh/o/submit` (SurveyMonkey: `https://www.surveymonkey.com/r/kane-cli-hackathon-submission`)  
Deadline: **Thu Nov 19, 2026 · 11:59 PM IST (10:29 AM PT)**

---

## Survey Questions (Copy & Paste)

1. **Solo or team?**  
   `Solo` (or update with teammate names if submitting as a team)

2. **Did you sign up on TestMu AI and claim your 10,000 free Kane CLI credits before building the project?**  
   `Yes` (registered TestMu AI account `lovesidhuy`, `@testmuai/kane-cli` v0.10.4)

3. **What is your name or your team members' names?**  
   `Lovepreet Sidhu`

4. **Emails of your teammates, or, if "Solo," write yours.**  
   `<your TestMu AI account email>`

5. **What is your GitHub repository link?**  
   `https://github.com/lovesidhuy/kane-ats-verifier`

6. **What is your demo video link (YouTube unlisted or Drive)?**  
   `<paste 3-5 min YouTube unlisted link recorded with DEMO_SCRIPT.md>`

7. **One-paragraph description of your project (what you built, which coding agent you used, and what Kane CLI verifies):**  
   > We built **Kane ATS Verifier** (`ats_verifier/` + `tests/kane/harness.py` + `scripts/kane_loop.py`), a closed-loop browser verification and self-healing system for multi-portal ATS job application agents, developed with **Cursor** (Claude/Gemini/Grok coding agents). Rather than trusting an autofill agent to submit blindly, every application flow across 7 ATS layouts, 10 candidate personas, and adversarial DOM/policy variants runs behind a dry-run network no-submit guard and is verified end-to-end by **Kane CLI** (`@testmuai/kane-cli` v0.10.4). When Kane CLI fails an assertion—such as a `500` list-index crash on strict personas, a `415` dedupe POST mismatch (`K-16`), or wrong visa/email/salary screening answers (`CL-2` / `CL-4`)—`kane_loop.py` parses Kane's NDJSON stream and packed `failure.yaml`, generates a deterministic `FixPlan` (`harness_patch` or `.loop_agent_policy.json` override), and re-runs Kane until the suite passes, exporting 54 indexed `.testmd` suites, 45 sealed L1 `.evidence` packs, 22 recorded loop runs, and 190 reward-filtered browser trajectories (50 public sample).

8. **Live URL or install command:**  
   ```bash
   git clone https://github.com/lovesidhuy/kane-ats-verifier.git && cd kane-ats-verifier && pip install -r requirements.txt && ./scripts/run_kane_verify.sh demo
   ```

9. **Which lane does your project fit?**  
   `Apps that prove themselves` / `Workflows with a spine` (Closed-loop verification & self-healing agent workflow)

10. **Which coding agents did you use?**  
    `Cursor`

---

## Required Launch Buzz (At Least 2 Public Posts)

Ready-to-post copy is in `SOCIAL_POSTS.md` (X/Twitter + LinkedIn). Add your demo video link before posting.
