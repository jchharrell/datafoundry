from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
from datetime import datetime, timezone
import pandas as pd

from .contracts import DataContract, ContractViolation


@dataclass(frozen=True)
class LineageReceipt:
    run_id: str
    input_rows: int
    accepted_rows: int
    quarantined_rows: int
    input_fingerprint: str
    output_fingerprint: str
    generated_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def _fingerprint(frame: pd.DataFrame) -> str:
    payload = frame.sort_index(axis=1).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def apply_quality_gate(frame: pd.DataFrame, contract: DataContract) -> tuple[pd.DataFrame, pd.DataFrame, list[ContractViolation], LineageReceipt]:
    violations = contract.validate(frame)
    bad_indices = sorted({v.row_index for v in violations})
    accepted = frame.drop(index=bad_indices).reset_index(drop=True)
    quarantined = frame.loc[bad_indices].copy().reset_index(drop=True) if bad_indices else frame.iloc[0:0].copy()
    run_material = json.dumps({"input": _fingerprint(frame), "rows": len(frame)}, sort_keys=True).encode()
    run_id = hashlib.sha256(run_material).hexdigest()[:12]
    receipt = LineageReceipt(
        run_id=run_id,
        input_rows=len(frame),
        accepted_rows=len(accepted),
        quarantined_rows=len(quarantined),
        input_fingerprint=_fingerprint(frame),
        output_fingerprint=_fingerprint(accepted),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    return accepted, quarantined, violations, receipt
