---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/linkedin?persona=international_coop&variant=strict_policy_screening
tags: [tier2, persona, international-coop, strict, linkedin]
max_steps: 25
---

# Tier 2 Persona Matrix — International Co-op on Strict LinkedIn

## Step 1: Open Strict LinkedIn Form for International Co-op
Navigate to http://127.0.0.1:8766/ats/linkedin?persona=international_coop&variant=strict_policy_screening.
Assert that "persona=international_coop" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Policy Fields & Safety Guard
Assert that input with id "first_name" has value "Arjun".
Assert that select with id "work_auth" has value "No".
Assert that select with id "sponsorship" has value "Yes".
Assert that input with id "salary_expectation" has value "65000".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
