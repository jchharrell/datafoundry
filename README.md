# DataFoundry

**A data-quality pipeline that treats bad records as evidence, not trash: explicit contracts, row-level violations, quarantine outputs, deterministic cleaning, and lineage receipts.**

Most cleaning demos end with `dropna()` and a prettier DataFrame. DataFoundry is built around a more production-minded question: **if a row is rejected, can another engineer tell exactly why, reproduce the decision, and prove which input produced the cleaned output?**

The package takes a CSV through a contract gate, separates accepted and quarantined records, writes structured violation reasons, cleans accepted data deterministically, and emits a lineage receipt with content fingerprints.

> Included datasets are synthetic and intentionally dirty.

## What makes this project different

### Data contracts with row-level evidence

`DataContract` defines required columns and validators. Instead of raising one generic “data invalid” error, it returns violations containing:

- row index
- column
- rule name
- offending value
- human-readable reason

That makes quality failures inspectable and lets downstream jobs decide whether to repair, quarantine, or stop.

### Quarantine instead of silent deletion

`apply_quality_gate()` splits the input into:

- **accepted records** that satisfy the contract
- **quarantined records** that violate one or more rules
- **violation metadata** explaining every rejection

Bad rows are preserved. That is important in real data systems because silently dropping records makes incidents hard to investigate.

### Lineage receipts

Every quality-gate run emits a `LineageReceipt` containing:

- deterministic run ID derived from the input
- input and output row counts
- quarantine count
- SHA-256-based input fingerprint
- SHA-256-based accepted-output fingerprint
- run timestamp

The fingerprint is not a blockchain or security product; it is a lightweight reproducibility mechanism. If the input changes, the receipt changes.

### Deterministic cleaning

Accepted rows then flow through `CleaningPipeline`, which normalizes email/state values, handles invalid ages, deduplicates customer IDs, sorts output deterministically, and emits a cleaning report.

## Architecture

```text
raw CSV
   |
   v
DataContract ---------> structured ContractViolation[]
   |
   v
quality_gate.py
   |                \
   |                 -> quarantine.csv
   |                 -> violations.json
   v
accepted rows
   |
   v
CleaningPipeline
   |
   +--> clean.csv
   +--> cleaning metrics
   +--> run_receipt.json (lineage + artifact paths)
```

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/jchharrell/datafoundry.git
cd datafoundry
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the included dirty customer file:

```bash
datafoundry examples/customers_dirty.csv --output demo-output
```

or:

```bash
python -m datafoundry.cli examples/customers_dirty.csv --output demo-output
```

You will get:

```text
demo-output/
├── clean.csv
├── quarantine.csv
├── violations.json
└── run_receipt.json
```

The CLI also prints the receipt summary to stdout, which makes it easy to use in a scheduled job or CI pipeline.

## Why the output files matter

A recruiter can inspect the project without trusting a screenshot:

- `clean.csv` shows what would be handed to downstream analytics or ML.
- `quarantine.csv` proves rejected records were preserved.
- `violations.json` explains each rejection programmatically.
- `run_receipt.json` ties the output back to the input fingerprint.

That makes the pipeline observable from the outside.

## Tests

```bash
pytest
```

The suite verifies:

- normalization and cleaning behavior
- missing-column failures
- duplicate handling
- row-level contract violations
- quarantine membership
- deterministic lineage IDs/fingerprints
- creation of CLI output artifacts

GitHub Actions installs the package and runs the suite on every push and pull request.

## Design decisions I can explain

**Why quarantine instead of dropping invalid rows?** Invalid data is often a symptom of an upstream bug. Preserving it gives data engineers something concrete to investigate and potentially replay after a fix.

**Why contracts before cleaning?** The contract represents what the downstream system promises to accept. Cleaning should not quietly invent meaning for data that violates a fundamental requirement.

**Why hash the data?** A short content fingerprint makes it easy to tell whether two runs started from the same bytes/values without storing another complete copy in metadata.

**Why Pandas?** This project focuses on quality semantics and pipeline structure. Pandas is familiar, easy to run locally, and appropriate for the small synthetic example. The same contract/quarantine idea could be implemented in Spark, Polars, dbt, or a warehouse.

## Production extensions

For production I would add configurable YAML/JSON contracts, severity levels (`warn` vs `reject`), schema versioning, partition-level metrics, object-store output, OpenTelemetry, data lineage integration, distributed execution, retry/idempotency behavior, and a repair/replay workflow for quarantined records.

## Interview walkthrough

See [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) for the project story, likely data-engineering questions, and tradeoffs.
