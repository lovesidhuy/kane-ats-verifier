"""Load the explicitly curated, integrity-checked official run manifest."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

KINDS = {"live_cli", "replay", "standalone_live_suite", "blocked_attempt"}

def load_official_runs(repo_root: Path) -> tuple[dict, dict]:
    directory = repo_root / "evidence" / "loop_runs"
    manifest = json.loads((directory / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("runs"), list):
        raise ValueError("invalid official run manifest schema")
    summaries = {}
    for entry in manifest["runs"]:
        run_id = entry["run_id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", run_id):
            raise ValueError(f"invalid official run id: {run_id!r}")
        if run_id in summaries:
            raise ValueError(f"duplicate official run: {run_id}")
        if entry.get("kind") not in KINDS or not entry.get("label", "").strip():
            raise ValueError(f"missing kind or label for official run: {run_id}")
        blob = (directory / run_id / "summary.json").read_bytes()
        if hashlib.sha256(blob).hexdigest() != entry.get("summary_sha256"):
            raise ValueError(f"official summary changed: {run_id}")
        summary = json.loads(blob)
        mode = summary.get("mode")
        if entry["kind"] == "replay" and mode != "replay":
            raise ValueError(f"official replay has wrong mode: {run_id}")
        if entry["kind"] == "live_cli" and mode != "live":
            raise ValueError(f"official live loop has wrong mode: {run_id}")
        summaries[run_id] = summary
    return manifest, summaries
