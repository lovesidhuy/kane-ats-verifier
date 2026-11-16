---
mode: testing
target: chrome
url: http://127.0.0.1:8766/tools/discovery-dedupe
tags: [tier2, discovery, deduplication]
max_steps: 20
---

# Tier 2 Discovery Deduplication & Apply-Type Classification

## Step 1: Run Cross-Board Discovery Deduplication
Navigate to http://127.0.0.1:8766/tools/discovery-dedupe.
Click the button "Run JobsFarm Discovery Deduplication".

## Step 2: Verify Deduplicated Output
Assert that "5" raw jobs, "3" unique jobs, and "2" duplicates removed are visible.
Assert that "Cloud Engineer" and "Platform SRE" are visible.
