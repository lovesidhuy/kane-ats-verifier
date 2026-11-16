---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=visa_sponsorship&variant=strict_policy_screening
tags: [tier2, policy-guardrails, visa-sponsorship, strict]
max_steps: 25
---

# Tier 2 High-Risk Policy Guardrails Verification

## Step 1: Open Strict Policy Screening Form
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=visa_sponsorship&variant=strict_policy_screening.
Assert that "persona=visa_sponsorship" and "variant=strict_policy_screening" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Policy Answers & Dry-Run Submission Guard
Assert that input with id "first_name" has value "Priya".
Assert that select with id "work_auth" has value "No".
Assert that select with id "sponsorship" has value "Yes".
Assert that input with id "salary_expectation" has value "160000".
Assert that select with id "security_clearance" has value "No".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
