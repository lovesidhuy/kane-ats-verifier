---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=devops_contractor&variant=mutated_ids
tags: [tier2, persona, devops, mutated-dom, greenhouse]
max_steps: 25
---

# Tier 2 Persona Matrix — DevOps Contractor on Mutated Greenhouse

## Step 1: Open Mutated Greenhouse Form
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=devops_contractor&variant=mutated_ids.
Assert that "persona=devops_contractor" and "variant=mutated_ids" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Elena".
Assert that input with id "fld_3c4m" has value "elena.rostova@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
