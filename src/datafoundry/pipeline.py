from __future__ import annotations
from dataclasses import dataclass, asdict
import pandas as pd
from .rules import normalize_email, normalize_state, valid_age

REQUIRED = ("customer_id", "email", "age", "state")

@dataclass(frozen=True)
class CleaningReport:
    input_rows: int
    output_rows: int
    duplicates_removed: int
    invalid_emails: int
    invalid_ages: int
    unknown_states: int

    def to_dict(self):
        return asdict(self)

class CleaningPipeline:
    """Deterministic customer-data cleaning with an auditable report."""

    def clean(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        missing = [c for c in REQUIRED if c not in frame.columns]
        if missing:
            raise ValueError(f"missing required columns: {missing}")

        df = frame.copy()
        input_rows = len(df)
        duplicate_mask = df.duplicated(subset=["customer_id"], keep="first")
        duplicates = int(duplicate_mask.sum())
        df = df.loc[~duplicate_mask].copy()

        normalized_email = df["email"].map(normalize_email)
        invalid_emails = int(normalized_email.isna().sum())
        df["email"] = normalized_email

        age_ok = df["age"].map(valid_age)
        invalid_ages = int((~age_ok).sum())
        df.loc[~age_ok, "age"] = pd.NA
        df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")

        normalized_state = df["state"].map(normalize_state)
        unknown_states = int(normalized_state.isna().sum())
        df["state"] = normalized_state

        df = df.sort_values("customer_id").reset_index(drop=True)
        report = CleaningReport(input_rows, len(df), duplicates, invalid_emails, invalid_ages, unknown_states)
        return df, report
