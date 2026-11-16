---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/indeed?persona=visa_sponsorship&variant=standard
tags: [tier2, persona, visa-sponsorship, indeed]
max_steps: 25
---

# Tier 2 Persona Matrix — Visa Sponsorship on Indeed SmartApply

## Step 1: Open Indeed SmartApply Form
Navigate to http://127.0.0.1:8766/ats/indeed?persona=visa_sponsorship&variant=standard.
Assert that "persona=visa_sponsorship" is visible.

## Step 2: Execute JobsFarm DOMAutofillEngine
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.

## Step 3: Verify Fields & Safety Guard
Assert that input with id "first_name" has value "Priya".
Assert that input with id "email" has value "priya.patel@example.com".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
