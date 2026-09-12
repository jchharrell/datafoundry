from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

from .contracts import customer_contract
from .pipeline import CleaningPipeline
from .quality_gate import apply_quality_gate


def run(input_path: str, output_dir: str) -> dict:
    source = Path(input_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(source)
    contract = customer_contract()
    accepted, quarantined, violations, receipt = apply_quality_gate(raw, contract)
    cleaned, cleaning_report = CleaningPipeline().clean(accepted) if len(accepted) else (accepted.copy(), None)

    cleaned.to_csv(destination / "clean.csv", index=False)
    quarantined.to_csv(destination / "quarantine.csv", index=False)
    (destination / "violations.json").write_text(
        json.dumps([v.to_dict() for v in violations], indent=2, default=str), encoding="utf-8"
    )
    summary = {
        "lineage": receipt.to_dict(),
        "cleaning": None if cleaning_report is None else cleaning_report.to_dict(),
        "files": {
            "clean": str(destination / "clean.csv"),
            "quarantine": str(destination / "quarantine.csv"),
            "violations": str(destination / "violations.json"),
        },
    }
    (destination / "run_receipt.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an auditable DataFoundry quality gate and cleaning pipeline")
    parser.add_argument("input", help="CSV file to inspect")
    parser.add_argument("--output", default="datafoundry-output", help="directory for clean/quarantine artifacts")
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
