#!/usr/bin/env python3
"""V-4: index suites with statuses from packs, loop_runs, and live recordings."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SUITE_DIR = REPO_ROOT / "tests" / "kane"
LOOP_DIR = REPO_ROOT / "evidence" / "loop_runs"
EVIDENCE_DIR = REPO_ROOT / "evidence"
sys.path.insert(0, str(REPO_ROOT))
from ats_verifier.official_runs import load_official_runs


def _overall_from_ndjson(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "test_md_done":
            return str(obj.get("overall_status") or "")
    return None


def _status_from_evidence_pack(pack: Path) -> tuple[str | None, str | None]:
    try:
        with zipfile.ZipFile(pack) as zf:
            for name in zf.namelist():
                if name.endswith("result.yaml") and "/tests/" in name:
                    data = yaml.safe_load(zf.read(name).decode("utf-8", errors="replace"))
                    if isinstance(data, dict):
                        st = str(data.get("overall_status") or data.get("status") or "")
                        test_id = name.split("/tests/")[1].split("/")[0] if "/tests/" in name else None
                        return st or None, test_id
            if "failure.yaml" in zf.namelist():
                return "failed", None
    except (zipfile.BadZipFile, OSError, yaml.YAMLError):
        return None, None
    return None, None


def build_index() -> dict:
    suite_status: dict[str, dict] = {}
    for path in sorted(SUITE_DIR.glob("*_test.md")):
        rel = str(path.relative_to(REPO_ROOT))
        suite_status[rel] = {
            "suite": rel,
            "url": None,
            "pack_in_repo": None,
            "status": "not_run",
            "source": None,
        }
        url_match = re.search(r"^url:\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
        if url_match:
            suite_status[rel]["url"] = url_match.group(1).strip()

    _manifest, loop_runs = load_official_runs(REPO_ROOT)
    for run_id in sorted(loop_runs):
        run_dir = LOOP_DIR / run_id
        summary = run_dir / "summary.json"
        ndjson = run_dir / "kane.ndjson"
        attempt1 = run_dir / "attempt_1" / "kane.ndjson"
        suite_path = None
        status = None
        if summary.is_file():
            data = json.loads(summary.read_text(encoding="utf-8"))
            suite_path = data.get("suite")
            if data.get("passed") is True:
                status = "passed"
            elif data.get("overall_status"):
                status = str(data["overall_status"])
            elif isinstance(data.get("attempts"), list) and data["attempts"]:
                status = str(data["attempts"][-1].get("overall_status") or "failed")
        if not status and ndjson.is_file():
            status = _overall_from_ndjson(ndjson)
            suite_path = suite_path or (json.loads(summary.read_text()).get("suite") if summary.is_file() else None)
        if not status and attempt1.is_file():
            status = _overall_from_ndjson(attempt1)
        if suite_path and suite_path in suite_status and status:
            suite_status[suite_path]["status"] = status
            suite_status[suite_path]["source"] = f"loop_runs/{run_dir.name}"

    for pack in sorted(EVIDENCE_DIR.glob("*.evidence")):
        st, _tid = _status_from_evidence_pack(pack)
        if not st:
            continue
        name = pack.stem
        for rel in suite_status:
            num = rel.split("/")[-1].split("_")[0]
            if num and num in name:
                suite_status[rel]["pack_in_repo"] = pack.name
                if suite_status[rel]["status"] == "not_run":
                    suite_status[rel]["status"] = st
                    suite_status[rel]["source"] = pack.name


    return {
        "suite_count": len(suite_status),
        "suites": list(suite_status.values()),
        "loop_runs": loop_runs,
        "sealed_packs_committed": len(list(EVIDENCE_DIR.glob("*.evidence"))),
    }


def main() -> None:
    index = build_index()
    out = EVIDENCE_DIR / "evidence_index.json"
    out.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(out), "suite_count": index["suite_count"]}, indent=2))


if __name__ == "__main__":
    main()