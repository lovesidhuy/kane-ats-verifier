---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/bamboohr?persona=security_analyst&variant=standard
tags: [tier2, persona, security-analyst, bamboohr]
max_steps: 25
---

# Tier 2 Persona Matrix — Security Analyst on BambooHR

## Step 1: Open BambooHR Form
Navigate to http://127.0.0.1:8766/ats/bamboohr?persona=security_analyst&variant=standard.
Assert that "persona=security_analyst" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Devon".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
