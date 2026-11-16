---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/workopolis?persona=qa_automation&variant=strict_policy_screening
tags: [tier2, persona, qa-automation, workopolis]
max_steps: 25
---

# Tier 2 Persona Matrix — QA Automation on Strict Workopolis

## Step 1: Open Strict Workopolis Form
Navigate to http://127.0.0.1:8766/ats/workopolis?persona=qa_automation&variant=strict_policy_screening.
Assert that "persona=qa_automation" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Hannah".
Assert that input with id "salary_expectation" has value "120000".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
