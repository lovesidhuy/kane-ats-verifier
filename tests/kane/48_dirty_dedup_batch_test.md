---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/discovery-dedupe
tags: [tier2, discovery, dirty-dedup]
max_steps: 20
---

# Tier 2 Dirty Cross-Board Discovery Deduplication

## Step 1: Run Dirty Batch Deduplication
Navigate to http://127.0.0.1:8766/tools/discovery-dedupe.
Click the button "Run JobsFarm Discovery Deduplication".

## Step 2: Verify Unique Normalized Jobs
Assert that "Cloud Engineer", "Platform SRE", and "IT Systems Admin" are visible.
