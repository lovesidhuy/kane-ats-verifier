---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever?persona=new_grad&variant=mutated_ids
tags: [tier2, persona, new-grad, mutated-dom, lever]
max_steps: 25
---

# Tier 2 Persona Matrix — New Grad on Mutated Lever DOM

## Step 1: Open Mutated Lever Form for New Grad
Navigate to http://127.0.0.1:8766/ats/lever?persona=new_grad&variant=mutated_ids.
Assert that "persona=new_grad" and "variant=mutated_ids" are visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Mutated Fields & Safety Guard
Assert that input with id "fld_9a1x" has value "Alex".
Assert that input with id "fld_3c4m" has value "alex.chen@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
