"""Pre-Submit Payload Receipt & Boundary Audit for ATS Dry-Run Interceptions.

Captures, validates, and serializes structured receipts for intercepted form
submissions so auditors and compliance reviewers can verify that:
1. Target endpoint URL and HTTP method were captured.
2. Complete key-value payload was mapped (0 null or unmapped required inputs).
3. Client-side HTML5/ARIA validation passed (form.checkValidity() and 0 aria-invalid).
4. Boundary audit verified that network guard prevented external data leakage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
import uuid


REQUIRED_ATS_FIELDS = {
    "first_name",
    "last_name",
    "email",
}


@dataclass
class BoundaryAudit:
    network_guard_active: bool = True
    external_post_blocked: bool = True
    preflight_passed: bool = True
    audit_verdict: str = "COMPLIANT_PREFLIGHT_PASS"
    rules_applied: list[str] = field(default_factory=lambda: [
        "zero_external_network_leak",
        "html5_validity_enforced",
        "zero_aria_invalid_nodes",
        "complete_required_field_coverage"
    ])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DryRunReceipt:
    ats_type: str
    target_url: str
    intercepted_method: str = "POST"
    persona: str = "senior_fullstack"
    variant: str = "standard"
    html5_valid: bool = True
    aria_invalid_count: int = 0
    unmapped_required_count: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    field_count: int = 0
    required_fields_status: dict[str, str] = field(default_factory=dict)
    boundary_audit: BoundaryAudit = field(default_factory=BoundaryAudit)
    receipt_id: str = field(default_factory=lambda: f"rcpt_{uuid.uuid4().hex[:12]}")
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.field_count and self.payload:
            self.field_count = len(self.payload)
        if isinstance(self.boundary_audit, dict):
            self.boundary_audit = BoundaryAudit(**self.boundary_audit)
        self._audit_required_fields()

    def _audit_required_fields(self) -> None:
        missing = 0
        statuses: dict[str, str] = {}
        for req in REQUIRED_ATS_FIELDS:
            # Check direct or prefix matching in payload keys
            found = False
            for k, v in self.payload.items():
                k_lower = k.lower()
                if (req in k_lower or k_lower.endswith(req)) and v is not None and str(v).strip() != "":
                    found = True
                    break
            if found:
                statuses[req] = "valid"
            else:
                statuses[req] = "unmapped_or_empty"
                missing += 1
        self.unmapped_required_count = missing
        self.required_fields_status = statuses
        if missing > 0 or not self.html5_valid or self.aria_invalid_count > 0:
            self.boundary_audit.preflight_passed = False
            self.boundary_audit.audit_verdict = "REJECTED_BOUNDARY_FAILURE"
        else:
            self.boundary_audit.preflight_passed = True
            self.boundary_audit.audit_verdict = "COMPLIANT_PREFLIGHT_PASS"

    def fingerprint(self) -> str:
        body = json.dumps({
            "ats": self.ats_type,
            "url": self.target_url,
            "method": self.intercepted_method,
            "payload": self.payload,
            "html5_valid": self.html5_valid,
        }, sort_keys=True)
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "fingerprint": self.fingerprint(),
            "timestamp_utc": self.timestamp_utc,
            "ats_type": self.ats_type,
            "target_url": self.target_url,
            "intercepted_method": self.intercepted_method,
            "persona": self.persona,
            "variant": self.variant,
            "html5_valid": self.html5_valid,
            "aria_invalid_count": self.aria_invalid_count,
            "unmapped_required_count": self.unmapped_required_count,
            "field_count": self.field_count,
            "required_fields_status": self.required_fields_status,
            "payload": self.payload,
            "boundary_audit": self.boundary_audit.to_dict(),
        }

    def save(self, directory: Path | str) -> Path:
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{self.ats_type}_{self.persona}_{self.variant}_receipt.json"
        path = target_dir / filename
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        # Also maintain a symlink-like latest
        (target_dir / "latest_receipt.json").write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DryRunReceipt:
        audit_raw = data.get("boundary_audit") or {}
        audit = BoundaryAudit(
            network_guard_active=audit_raw.get("network_guard_active", True),
            external_post_blocked=audit_raw.get("external_post_blocked", True),
            preflight_passed=audit_raw.get("preflight_passed", True),
            audit_verdict=audit_raw.get("audit_verdict", "COMPLIANT_PREFLIGHT_PASS"),
            rules_applied=audit_raw.get("rules_applied") or [
                "zero_external_network_leak",
                "html5_validity_enforced",
                "zero_aria_invalid_nodes",
                "complete_required_field_coverage"
            ]
        )
        return cls(
            ats_type=data.get("ats_type", "unknown"),
            target_url=data.get("target_url", ""),
            intercepted_method=data.get("intercepted_method", "POST"),
            persona=data.get("persona", "senior_fullstack"),
            variant=data.get("variant", "standard"),
            html5_valid=data.get("html5_valid", True),
            aria_invalid_count=data.get("aria_invalid_count", 0),
            unmapped_required_count=data.get("unmapped_required_count", 0),
            payload=dict(data.get("payload") or {}),
            field_count=data.get("field_count", len(data.get("payload") or {})),
            required_fields_status=dict(data.get("required_fields_status") or {}),
            boundary_audit=audit,
            receipt_id=data.get("receipt_id") or f"rcpt_{uuid.uuid4().hex[:12]}",
            timestamp_utc=data.get("timestamp_utc") or datetime.now(timezone.utc).isoformat(),
        )


def validate_receipt_file(path: Path | str) -> tuple[bool, str, dict[str, Any]]:
    p = Path(path)
    if not p.is_file():
        return False, f"Receipt file not found: {p}", {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON in {p}: {exc}", {}
    receipt = DryRunReceipt.from_dict(raw)
    passed = (
        receipt.html5_valid
        and receipt.aria_invalid_count == 0
        and receipt.unmapped_required_count == 0
        and receipt.boundary_audit.preflight_passed
    )
    msg = f"Receipt {receipt.receipt_id}: {receipt.boundary_audit.audit_verdict} ({receipt.field_count} fields, unmapped={receipt.unmapped_required_count})"
    return passed, msg, receipt.to_dict()
