"""Regression: discovery dedupe UI must POST JSON Flask accepts (K-16)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "tests" / "kane" / "harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("kane_harness", HARNESS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_dedupe_post_matches_ui_after_k16_fix():
    """Same shape as runDedupe() in DISCOVERY_HTML after the Content-Type fix."""
    mod = _load_harness()
    client = mod.app.test_client()
    res = client.post(
        "/api/run-dedupe",
        data="{}",
        content_type="application/json",
    )
    assert res.status_code == 200, res.get_data(as_text=True)
    data = res.get_json()
    assert isinstance(data, dict)
    for key in ("raw_count", "unique_count", "duplicates_removed", "jobs"):
        assert key in data
    assert isinstance(data["jobs"], list)
    assert data["raw_count"] >= data["unique_count"]


def test_run_dedupe_bare_post_was_415_k16_regression():
    """Documents the bug Kane caught: empty POST with no Content-Type."""
    mod = _load_harness()
    client = mod.app.test_client()
    res = client.post("/api/run-dedupe")
    # Server now tolerates silent JSON; must not return 415.
    assert res.status_code != 415