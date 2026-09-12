from pathlib import Path
import json
import pandas as pd

from datafoundry.cli import run
from datafoundry.contracts import customer_contract
from datafoundry.quality_gate import apply_quality_gate


def sample_frame():
    return pd.DataFrame(
        [
            {"customer_id": "C1", "email": "a@example.com", "age": 30, "state": "NC"},
            {"customer_id": "C2", "email": "broken-email", "age": 44, "state": "SC"},
            {"customer_id": "C3", "email": "c@example.com", "age": 180, "state": "VA"},
            {"customer_id": "C4", "email": "d@example.com", "age": 22, "state": "XX"},
        ]
    )


def test_quality_gate_quarantines_bad_rows_and_keeps_reason():
    accepted, quarantined, violations, receipt = apply_quality_gate(sample_frame(), customer_contract())
    assert accepted["customer_id"].tolist() == ["C1"]
    assert set(quarantined["customer_id"]) == {"C2", "C3", "C4"}
    assert {v.rule for v in violations} == {"email_shape", "age_range", "known_state"}
    assert receipt.accepted_rows == 1
    assert receipt.quarantined_rows == 3


def test_lineage_receipt_is_deterministic_for_same_input_except_timestamp():
    first = apply_quality_gate(sample_frame(), customer_contract())[3]
    second = apply_quality_gate(sample_frame(), customer_contract())[3]
    assert first.run_id == second.run_id
    assert first.input_fingerprint == second.input_fingerprint
    assert first.output_fingerprint == second.output_fingerprint


def test_cli_produces_handoff_artifacts(tmp_path: Path):
    source = tmp_path / "dirty.csv"
    sample_frame().to_csv(source, index=False)
    output = tmp_path / "out"
    summary = run(str(source), str(output))
    assert (output / "clean.csv").exists()
    assert (output / "quarantine.csv").exists()
    assert (output / "violations.json").exists()
    assert (output / "run_receipt.json").exists()
    receipt = json.loads((output / "run_receipt.json").read_text())
    assert receipt["lineage"]["quarantined_rows"] == 3
    assert summary["lineage"]["accepted_rows"] == 1
