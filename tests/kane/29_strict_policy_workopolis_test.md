---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/workopolis?persona=new_grad&variant=strict_policy_screening
tags: [tier2, strict, new-grad, workopolis]
max_steps: 25
---

# Tier 2 Strict Policy — New Grad on Workopolis

## Step 1: Open Strict Workopolis Form
Navigate to http://127.0.0.1:8766/ats/workopolis?persona=new_grad&variant=strict_policy_screening.
Assert that "persona=new_grad" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Strict Fields & Safety Guard
Assert that input with id "first_name" has value "Alex".
Assert that input with id "salary_expectation" has value "85000".
Assert that select with id "security_clearance" has value "No".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
