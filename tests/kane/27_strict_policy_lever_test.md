---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever?persona=devops_contractor&variant=strict_policy_screening
tags: [tier2, strict, devops, lever]
max_steps: 25
---

# Tier 2 Strict Policy — DevOps Contractor on Lever

## Step 1: Open Strict Lever Form
Navigate to http://127.0.0.1:8766/ats/lever?persona=devops_contractor&variant=strict_policy_screening.
Assert that "persona=devops_contractor" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Strict Fields & Safety Guard
Assert that input with id "first_name" has value "Elena".
Assert that input with id "salary_expectation" has value "175000".
Assert that select with id "security_clearance" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
