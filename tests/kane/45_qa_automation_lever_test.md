---
mode: testing
target: chrome
url: http://127.0.0.1:8766/ats/lever?persona=qa_automation&variant=standard
tags: [tier2, persona, qa-automation, lever]
max_steps: 25
---

# Tier 2 Persona Matrix — QA Automation on Lever

## Step 1: Open Lever Form
Navigate to http://127.0.0.1:8766/ats/lever?persona=qa_automation&variant=standard.
Assert that "persona=qa_automation" is visible.

## Step 2: Execute DOMAutofillEngine & Verify
Click the button "Run JobsFarm DOMAutofillEngine".
Assert that "AUTOFILL_COMPLETED" is visible on the page.
Assert that input with id "first_name" has value "Hannah".
Click the button "Submit Application".
Assert that "SAFETY_GUARD_ACTIVE" is visible.
