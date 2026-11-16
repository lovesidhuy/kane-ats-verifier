---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/workopolis?persona=devops_contractor&variant=standard
tags: [tier2, persona, devops, workopolis]
max_steps: 25
---

# Tier 2 Persona Matrix — DevOps Contractor on Workopolis

## Step 1: Open Workopolis Form
Navigate to http://127.0.0.1:8766/ats/workopolis?persona=devops_contractor&variant=standard.
Assert that "persona=devops_contractor" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Elena".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
