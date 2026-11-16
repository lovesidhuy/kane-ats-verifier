"""Unit test for Hugging Face trajectory dataset evaluation."""

from pathlib import Path
from scripts.eval_trajectories import evaluate_dataset, validate_trajectory_record

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_eval_trajectories_sample_50():
    sample_file = REPO_ROOT / "evidence" / "verified_trajectories_sample_50.jsonl"
    assert sample_file.is_file()
    stats = evaluate_dataset(sample_file)
    assert stats["total_records"] == 50
    assert stats["schema_compliance_pct"] == 100.0
    assert len(stats["errors"]) == 0
    assert stats["reward_filtering"]["reward_score"] == 1.0
    assert stats["actions_summary"]["total_actions"] > 500
    assert len(stats["distributions"]["ats_platforms"]) >= 7


def test_validate_record_catches_invalid():
    bad_row = {
        "source_type": "invalid_type",
        "evidence_pack_id": "foo.evidence",
        # missing fields
    }
    errs = validate_trajectory_record(bad_row, 1)
    assert len(errs) > 0
    assert any("missing required field" in e for e in errs)
    assert any("invalid source_type" in e for e in errs)
