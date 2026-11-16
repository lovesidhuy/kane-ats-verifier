#!/usr/bin/env python3
"""P0-5: scan workspace (not full git history) for likely secrets and large blobs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PATTERNS = [
    (re.compile(r"LT_ACCESS_KEY\s*=\s*['\"]?[A-Za-z0-9]{20,}"), "LT_ACCESS_KEY assignment"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI-style key"),
    (re.compile(r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}['\"]", re.I), "generic api_key"),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".testmuai"}
MAX_FILE_MB = 5.0


def scan_tree() -> dict:
    hits: list[dict] = []
    large: list[dict] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in {".png", ".jpg", ".webm", ".evidence", ".zip"}:
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > MAX_FILE_MB:
                large.append({"path": str(path.relative_to(REPO_ROOT)), "size_mb": round(size_mb, 2)})
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern, label in PATTERNS:
                if pattern.search(line):
                    hits.append(
                        {
                            "path": str(path.relative_to(REPO_ROOT)),
                            "line": line_no,
                            "kind": label,
                        }
                    )
    gitignored_testmuai = (REPO_ROOT / ".testmuai").exists()
    return {
        "secret_pattern_hits": hits,
        "large_files_mb_gt_5": large,
        "local_dot_testmuai_present": gitignored_testmuai,
        "note": "Full history scan: run `git log --all -p` locally; this script scans working tree only.",
    }


def main() -> int:
    report = scan_tree()
    try:
        hist = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        report["recent_commits"] = (hist.stdout or "").strip().splitlines()
    except FileNotFoundError:
        report["recent_commits"] = []
    out_path = REPO_ROOT / "evidence" / "p0_5_secrets_scan.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report["secret_pattern_hits"] else 0


if __name__ == "__main__":
    sys.exit(main())