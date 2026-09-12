# DataFoundry Architecture

DataFoundry is a Pandas-based data-quality and ETL project built around explicit contracts, quarantine workflows, reproducibility, and lineage.

## Design goals

- validate incoming data before silently normalizing it
- preserve rejected rows as debugging evidence
- keep data-quality rules explicit and testable
- make repeated runs deterministic and inspectable
- emit artifacts that downstream systems can consume

## Contract layer

`contracts.py` defines required columns and validation rules as code. This keeps expectations versionable and reviewable instead of burying assumptions in ad hoc notebook cells.

## Quality gate

`quality_gate.py` separates accepted rows from quarantined rows and records structured violation details. The design intentionally avoids deleting invalid records because rejected rows are useful evidence when tracing upstream failures.

Each run also emits fingerprints and a deterministic receipt so the exact input/output relationship can be inspected later.

## Cleaning pipeline

`pipeline.py` performs deterministic normalization and deduplication after validation. Accepted records are transformed without mutating the caller's original DataFrame.

The project treats validation and cleaning as different responsibilities: validation decides whether a row satisfies the contract; cleaning standardizes known representations without inventing missing meaning.

## CLI artifacts

The command-line workflow produces:

- `clean.csv`
- `quarantine.csv`
- `violations.json`
- `run_receipt.json`

This makes DataFoundry usable as a pipeline component rather than only as notebook code.

## Scaling path

The current implementation uses Pandas for readability and local execution. The same contract/quarantine/lineage pattern could be moved to Polars, Spark, SQL/dbt, or a warehouse-native quality layer while preserving the reporting semantics.

## Verification

Pytest covers cleaning, validation, quarantine decisions, lineage fingerprints, and generated CLI artifacts. GitHub Actions installs the package, executes the test suite, and smoke-tests the CLI output files.

## Scope

The included rules and example datasets are synthetic. The project demonstrates data-quality engineering patterns rather than prescribing universal validation rules or replacing an enterprise observability platform.