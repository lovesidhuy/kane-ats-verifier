---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby?persona=product_manager&variant=strict_policy_screening
tags: [tier2, persona, product-manager, strict, ashby]
max_steps: 25
---

# Tier 2 Persona Matrix — Product Manager on Strict Ashby

## Step 1: Open Strict Ashby Form for Product Manager
Navigate to http://127.0.0.1:8766/ats/ashby?persona=product_manager&variant=strict_policy_screening.
Assert that "persona=product_manager" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Fields & Safety Guard
Assert that input with id "first_name" has value "Liam".
Assert that input with id "salary_expectation" has value "155000".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
