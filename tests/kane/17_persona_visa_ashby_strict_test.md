---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/ashby?persona=visa_sponsorship&variant=strict_policy_screening
tags: [tier2, persona, visa-sponsorship, strict, ashby]
max_steps: 25
---

# Tier 2 Persona Matrix — Visa Sponsorship on Strict Ashby

## Step 1: Open Strict Ashby Form for Visa Applicant
Navigate to http://127.0.0.1:8766/ats/ashby?persona=visa_sponsorship&variant=strict_policy_screening.
Assert that "persona=visa_sponsorship" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Strict Fields & Safety Guard
Assert that input with id "first_name" has value "Priya".
Assert that select with id "sponsorship" has value "Yes".
Assert that input with id "salary_expectation" has value "160000".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
