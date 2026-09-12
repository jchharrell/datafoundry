from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Callable, Iterable
import pandas as pd


@dataclass(frozen=True)
class ContractViolation:
    row_index: int
    column: str
    rule: str
    value: object
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ColumnContract:
    name: str
    nullable: bool = True
    validator: Callable[[object], bool] | None = None
    rule_name: str = "custom"


class DataContract:
    """Small, explicit schema contract that returns row-level violations.

    Unlike a generic exception, violations retain the offending row, field,
    rule and value so bad records can be quarantined rather than silently
    discarded or allowed to poison downstream features.
    """

    def __init__(self, columns: Iterable[ColumnContract]):
        self.columns = tuple(columns)

    def validate(self, frame: pd.DataFrame) -> list[ContractViolation]:
        missing = [contract.name for contract in self.columns if contract.name not in frame.columns]
        if missing:
            raise ValueError(f"missing contracted columns: {missing}")

        violations: list[ContractViolation] = []
        for contract in self.columns:
            for index, value in frame[contract.name].items():
                is_missing = pd.isna(value)
                if is_missing and not contract.nullable:
                    violations.append(ContractViolation(int(index), contract.name, "not_null", value, "value is required"))
                    continue
                if is_missing:
                    continue
                if contract.validator is not None and not contract.validator(value):
                    violations.append(
                        ContractViolation(int(index), contract.name, contract.rule_name, value, f"value failed {contract.rule_name}")
                    )
        return violations


def customer_contract() -> DataContract:
    valid_states = {"NC", "SC", "VA", "GA", "FL", "NY", "CA", "TX", "AZ"}
    return DataContract(
        [
            ColumnContract("customer_id", nullable=False, validator=lambda x: bool(str(x).strip()), rule_name="non_blank_id"),
            ColumnContract("email", nullable=False, validator=lambda x: "@" in str(x) and "." in str(x).split("@")[-1], rule_name="email_shape"),
            ColumnContract("age", nullable=False, validator=lambda x: str(x).strip().lstrip("-").isdigit() and 0 <= int(x) <= 120, rule_name="age_range"),
            ColumnContract("state", nullable=False, validator=lambda x: str(x).strip().upper() in valid_states, rule_name="known_state"),
        ]
    )
