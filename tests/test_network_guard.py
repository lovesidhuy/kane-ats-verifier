"""Unit checks for harness network submit guard (P0-3)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_harness():
    harness_path = REPO_ROOT / "tests" / "kane" / "harness.py"
    spec = importlib.util.spec_from_file_location("jobsfarm_kane_harness_ng", harness_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_network_guard_page_renders_active():
    mod = _load_harness()
    client = mod.app.test_client()
    response = client.get("/tools/network-guard-test")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "networkGuard" in body or "NETWORK_SUBMIT_GUARD" in body
    assert 'data-networkGuard' in body or "network_guard_enabled" in body.lower() or "active" in body


def test_network_guard_disabled_query_off():
    mod = _load_harness()
    client = mod.app.test_client()
    response = client.get("/tools/network-guard-test?guard=off")
    body = response.get_data(as_text=True)
    assert "NETWORK_SUBMIT_GUARD_DISABLED" in body