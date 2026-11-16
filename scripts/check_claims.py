#!/usr/bin/env python3
"""Reconcile headline numbers vs evidence/index files and judge-facing docs."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DOC_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "HACKATHON_SUBMISSION.md",
    REPO_ROOT / "JUDGES.md",
    REPO_ROOT / "HANDOFF.txt",
    REPO_ROOT / "DEMO_SCRIPT.md",
    REPO_ROOT / "SOCIAL_POSTS.md",
]

STALE_PATTERNS = [
    r"10,843\.97",
    r"/Users/lovepreet",
    r"~/Downloads/",
    r"automation_monorepo",
]


def _required_snippets(sub: dict) -> list[tuple[str, str]]:
    return [
        ("suites_indexed", str(sub["suites_indexed"])),
        ("sealed_packs", str(sub["sealed_packs_committed"])),
        ("trajectories_total", str(sub["trajectories_total_claimed"])),
        ("trajectories_sample", str(sub["trajectories_sample_committed"])),
        ("loop_runs", str(sub["loop_runs_recorded"])),
        ("hackathon_pytest", str(sub["hackathon_pytest_count"])),
        ("credits_ledger", f"{sub['credits']['ledger_rows_sum']:.2f}".rstrip("0").rstrip(".")),
    ]


def _hackathon_pytest_count() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--collect-only",
        "-q",
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return 0
    m = re.search(r"(\d+) tests?", proc.stdout)
    return int(m.group(1)) if m else 0


def _credits_from_ledger() -> tuple[float, float]:
    path = REPO_ROOT / "evidence" / "credits_ledger.csv"
    if not path.is_file():
        return 0.0, 0.0
    rows_sum = 0.0
    first_before = None
    last_after = None
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows_sum += float(row["credits_recorded"])
            if first_before is None:
                first_before = float(row["balance_before"])
            last_after = float(row["balance_after"])
    delta = (first_before - last_after) if first_before is not None and last_after is not None else 0.0
    return round(rows_sum, 4), round(delta, 4)


CLAIM_REQUIRED_IN = {
    "README.md",
    "HACKATHON_SUBMISSION.md",
    "JUDGES.md",
    "HANDOFF.txt",
}


def _doc_scan(sub: dict) -> list[str]:
    errors: list[str] = []
    snippets = _required_snippets(sub)
    for path in DOC_FILES:
        if not path.is_file():
            errors.append(f"missing doc {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in STALE_PATTERNS:
            if re.search(pattern, text, re.I):
                errors.append(f"stale pattern {pattern!r} in {path.name}")
        if path.name not in CLAIM_REQUIRED_IN:
            continue
        for label, needle in snippets:
            if needle not in text:
                errors.append(f"{path.name}: missing canonical {label} (expected {needle!r})")
    return errors


def main() -> int:
    manifest_path = REPO_ROOT / "evidence" / "dataset_manifest.json"
    index_path = REPO_ROOT / "evidence" / "evidence_index.json"
    submission_path = REPO_ROOT / "SUBMISSION.json"

    errors: list[str] = []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {}

    if not index_path.is_file():
        errors.append("missing evidence/evidence_index.json — run scripts/evidence_index.py")

    ledger_sum, ledger_delta = _credits_from_ledger()
    pytest_h = _hackathon_pytest_count()
    if pytest_h < 1:
        errors.append("could not collect hackathon pytest count")

    submission = {
        "hackathon": "Kane CLI Online Hackathon",
        "repo_note": "Clean standalone hackathon artifact (initialized Nov 15, 2026)",
        "suites_indexed": index.get("suite_count"),
        "trajectories_total_claimed": manifest.get("total_verified_trajectories"),
        "trajectories_sample_committed": manifest.get("public_sample_count"),
        "loop_runs_recorded": len(index.get("loop_runs") or {}),
        "cl2_run_id": "cl2_visa_seed_live",
        "cl2_passed": (index.get("loop_runs") or {}).get("cl2_visa_seed_live", {}).get("passed"),
        "demo_run_id": "judge_demo",
        "sealed_packs_committed": index.get("sealed_packs_committed"),
        "hackathon_pytest_count": pytest_h,
        "replay_command": "./scripts/run_kane_verify.sh demo",
        "credits": {
            "ledger_rows_sum": ledger_sum,
            "ledger_balance_delta": ledger_delta,
            "footnote": (
                "ledger.csv totals recorded live Kane CLI loop runs across the hackathon sprint."
            ),
        },
    }
    submission_path.write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")

    if manifest.get("public_sample_count") is not None and int(manifest["public_sample_count"]) != 50:
        errors.append(f"sample trajectory count expected 50, got {manifest['public_sample_count']}")
    if manifest.get("total_verified_trajectories") is not None and int(manifest["total_verified_trajectories"]) != 162:
        errors.append(f"total trajectory claim expected 162, got {manifest['total_verified_trajectories']}")

    cl2 = (index.get("loop_runs") or {}).get("cl2_visa_seed_live")
    if cl2 and cl2.get("passed") is not True:
        errors.append("cl2_visa_seed_live summary says not passed")

    errors.extend(_doc_scan(submission))

    if errors:
        print(json.dumps({"ok": False, "errors": errors, "submission": submission}, indent=2))
        return 1
    print(json.dumps({"ok": True, "submission": submission}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
