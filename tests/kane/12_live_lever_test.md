---
mode: testing
target: chrome
url: https://jobs.lever.co/leverdemo
tags: [tier1, live-ats, lever, dry-run]
max_steps: 25
---

# Tier 1 Live Public Lever Demo Board Verification (Dry-Run)

## Step 1: Open Live Public Lever Demo Board & Navigate to Apply Form
Navigate to https://jobs.lever.co/leverdemo.
Click the first job posting link to open its details page, then click the "Apply for this job" button.
Assert that the URL contains "/apply".

## Step 2: Populate Core Candidate Fields (JobsFarm Profile Values)
Enter "Jane Doe" into the Full name input field (name "name").
Enter "user@example.com" into the Email input field (name "email").

## Step 3: Verify Populated Live DOM Inputs & Abort Before Submit
Assert that the Full name input field (name "name") has value "Jane Doe".
Assert that the Email input field (name "email") has value "user@example.com".
Do NOT click the Submit application button.
