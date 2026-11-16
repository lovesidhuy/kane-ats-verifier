---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=data_engineer&variant=strict_policy_screening
tags: [tier2, persona, data-engineer, strict, greenhouse]
max_steps: 25
---

# Tier 2 Persona Matrix — Data Engineer on Strict Greenhouse

## Step 1: Open Strict Greenhouse Form
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=data_engineer&variant=strict_policy_screening.
Assert that "persona=data_engineer" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Sofia".
Assert that input with id "salary_expectation" has value "140000".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
