import pandas as pd
import pytest
from datafoundry import CleaningPipeline


def dirty_frame():
    return pd.DataFrame([
        {"customer_id": 2, "email": " BAD ", "age": 150, "state": "North Carolina"},
        {"customer_id": 1, "email": " A@Example.com ", "age": 21, "state": "n.c."},
        {"customer_id": 1, "email": "duplicate@example.com", "age": 99, "state": "SC"},
        {"customer_id": 3, "email": "b@example.com", "age": "34", "state": "Virginia"},
    ])


def test_pipeline_is_deterministic_and_auditable():
    cleaned, report = CleaningPipeline().clean(dirty_frame())
    assert list(cleaned.customer_id) == [1, 2, 3]
    assert report.input_rows == 4
    assert report.output_rows == 3
    assert report.duplicates_removed == 1
    assert report.invalid_emails == 1
    assert report.invalid_ages == 1
    assert cleaned.loc[0, "email"] == "a@example.com"
    assert cleaned.loc[0, "state"] == "NC"


def test_input_frame_is_not_mutated():
    original = dirty_frame()
    before = original.copy(deep=True)
    CleaningPipeline().clean(original)
    pd.testing.assert_frame_equal(original, before)


def test_schema_contract_rejects_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        CleaningPipeline().clean(pd.DataFrame({"customer_id": [1]}))
