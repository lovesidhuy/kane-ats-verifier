---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=security_analyst&variant=strict_policy_screening
tags: [tier2, persona, security-analyst, strict, greenhouse]
max_steps: 25
---

# Tier 2 Persona Matrix — Security Analyst on Strict Greenhouse

## Step 1: Open Strict Greenhouse Form for Security Analyst
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=security_analyst&variant=strict_policy_screening.
Assert that "persona=security_analyst" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Fields & Safety Guard
Assert that input with id "first_name" has value "Devon".
Assert that input with id "salary_expectation" has value "130000".
Assert that select with id "security_clearance" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
