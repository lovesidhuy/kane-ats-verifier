---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/indeed?persona=international_coop&variant=strict_policy_screening
tags: [tier2, persona, international-coop, indeed]
max_steps: 25
---

# Tier 2 Persona Matrix — International Co-op on Strict Indeed

## Step 1: Open Strict Indeed Form
Navigate to http://127.0.0.1:8766/ats/indeed?persona=international_coop&variant=strict_policy_screening.
Assert that "persona=international_coop" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Arjun".
Assert that select with id "sponsorship" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
