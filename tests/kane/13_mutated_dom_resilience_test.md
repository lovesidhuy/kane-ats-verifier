---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=senior_fullstack&variant=mutated_ids
tags: [tier2, mutated-dom, resilience, greenhouse]
max_steps: 25
---

# Tier 2 Mutated DOM Resilience Verification (Randomized IDs)

## Step 1: Open Mutated Greenhouse ATS Form
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=senior_fullstack&variant=mutated_ids.
Assert that "variant=mutated_ids" is visible.

## Step 2: Execute DOMAutofillEngine on Randomized Field IDs
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Label-Based Resilience & Dry-Run Guard
Assert that input with id "fld_9a1x" has value "Jane".
Assert that input with id "fld_7b2z" has value "Doe".
Assert that input with id "fld_3c4m" has value "user@example.com".
Assert that select with id "fld_1g8w" has value "Yes".
Assert that select with id "fld_5h9r" has value "No".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
