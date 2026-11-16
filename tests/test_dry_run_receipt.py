"""Unit tests for Pre-Submit Payload Receipt & Boundary Audit."""

from pathlib import Path
import pytest
from ats_verifier.receipt import BoundaryAudit, DryRunReceipt, validate_receipt_file
from tests.kane.harness import app


def test_dry_run_receipt_compliant(tmp_path: Path):
    receipt = DryRunReceipt(
        ats_type="ashby",
        target_url="http://127.0.0.1:8766/ats/ashby",
        persona="senior_fullstack",
        variant="standard",
        html5_valid=True,
        aria_invalid_count=0,
        payload={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "user@example.com",
            "phone": "555-0100",
            "work_auth": "Yes",
            "sponsorship": "No",
        },
    )
    assert receipt.boundary_audit.preflight_passed is True
    assert receipt.boundary_audit.audit_verdict == "COMPLIANT_PREFLIGHT_PASS"
    assert receipt.unmapped_required_count == 0
    assert receipt.field_count == 6

    saved_path = receipt.save(tmp_path)
    assert saved_path.is_file()

    valid, msg, data = validate_receipt_file(saved_path)
    assert valid is True
    assert "COMPLIANT_PREFLIGHT_PASS" in msg
    assert data["field_count"] == 6


def test_dry_run_receipt_missing_required():
    receipt = DryRunReceipt(
        ats_type="lever",
        target_url="http://127.0.0.1:8766/ats/lever",
        html5_valid=True,
        aria_invalid_count=0,
        payload={
            "first_name": "Jane",
            # missing last_name and email
            "phone": "555-0100",
        },
    )
    assert receipt.boundary_audit.preflight_passed is False
    assert receipt.boundary_audit.audit_verdict == "REJECTED_BOUNDARY_FAILURE"
    assert receipt.unmapped_required_count == 2
    assert receipt.required_fields_status["email"] == "unmapped_or_empty"
    assert receipt.required_fields_status["last_name"] == "unmapped_or_empty"


def test_dry_run_receipt_aria_invalid():
    receipt = DryRunReceipt(
        ats_type="greenhouse",
        target_url="http://127.0.0.1:8766/ats/greenhouse",
        html5_valid=True,
        aria_invalid_count=1,
        payload={"first_name": "Jane", "last_name": "Doe", "email": "user@example.com"},
    )
    assert receipt.boundary_audit.preflight_passed is False
    assert receipt.boundary_audit.audit_verdict == "REJECTED_BOUNDARY_FAILURE"


def test_harness_receipt_endpoints():
    client = app.test_client()
    payload = {
        "ats_type": "bamboohr",
        "target_url": "http://127.0.0.1:8766/ats/bamboohr",
        "persona": "healthcare_ops",
        "variant": "strict_policy_screening",
        "html5_valid": True,
        "aria_invalid_count": 0,
        "payload": {
            "first_name": "Sarah",
            "last_name": "Connor",
            "email": "sarah.connor@example.com",
            "phone": "555-0199",
            "salary_expectation": "120000",
        },
    }
    resp = client.post("/api/dry-run-receipt", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["receipt"]["boundary_audit"]["audit_verdict"] == "COMPLIANT_PREFLIGHT_PASS"

    list_resp = client.get("/api/dry-run-receipts")
    assert list_resp.status_code == 200
    list_data = list_resp.get_json()
    assert list_data["count"] >= 1
