---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/indeed?persona=healthcare_ops&variant=strict_policy_screening
tags: [tier2, strict, healthcare-ops, indeed]
max_steps: 25
---

# Tier 2 Strict Policy — Healthcare Ops on Indeed SmartApply

## Step 1: Open Strict Indeed Form
Navigate to http://127.0.0.1:8766/ats/indeed?persona=healthcare_ops&variant=strict_policy_screening.
Assert that "persona=healthcare_ops" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Strict Fields & Safety Guard
Assert that input with id "first_name" has value "Marcus".
Assert that input with id "salary_expectation" has value "110000".
Assert that select with id "security_clearance" has value "Yes".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
