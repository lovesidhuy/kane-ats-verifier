---
mode: testing
target: chrome
url: https://job-boards.greenhouse.io/anthropic/jobs/5183044008
tags: [tier1, live-ats, greenhouse, dry-run]
max_steps: 25
---

# Tier 1 Live Public Greenhouse ATS Verification (Dry-Run)

## Step 1: Open Live Public Greenhouse Job Posting
Navigate to https://job-boards.greenhouse.io/anthropic/jobs/5183044008.
Assert that the application form input with id "first_name" is visible.
Assert that the application form input with id "last_name" is visible.
Assert that the application form input with id "email" is visible.

## Step 2: Populate Core Candidate Fields (JobsFarm Profile Values)
Enter "Jane" into the input with id "first_name".
Enter "Doe" into the input with id "last_name".
Enter "user@example.com" into the input with id "email".

## Step 3: Verify Populated Live DOM Inputs & Abort Before Submit
Assert that input with id "first_name" has value "Jane".
Assert that input with id "last_name" has value "Doe".
Assert that input with id "email" has value "user@example.com".
Do NOT click the submit application button.
