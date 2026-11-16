---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/greenhouse?persona=new_grad&variant=standard
tags: [tier2, persona, new-grad, greenhouse]
max_steps: 25
---

# Tier 2 Persona Matrix — New Grad Cloud/Network Engineer (Greenhouse)

## Step 1: Open Greenhouse Form for New Grad Persona
Navigate to http://127.0.0.1:8766/ats/greenhouse?persona=new_grad&variant=standard.
Assert that "persona=new_grad" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify New Grad Profile Values & Dry-Run Guard
Assert that input with id "first_name" has value "Alex".
Assert that input with id "last_name" has value "Chen".
Assert that input with id "email" has value "alex.chen@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
