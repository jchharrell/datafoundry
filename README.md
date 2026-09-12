# DataFoundry

An auditable data-quality pipeline for messy customer records. The project separates **profiling/validation rules** from **pipeline orchestration** so cleaning decisions are explicit, testable, and reproducible.

## Problems handled

- duplicate business keys
- malformed and inconsistently cased emails
- invalid ages and nullable integer typing
- inconsistent state labels such as `North Carolina`, `n.c.`, and `NC`
- missing required schema columns
- deterministic output ordering
- a structured cleaning report describing what changed

## Run the Python pipeline

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
python examples/run_pipeline.py
```

The example reads a deliberately dirty synthetic CSV, writes a cleaned version, and prints an audit report. The browser demo (`index.html`) provides a quick visual walkthrough.

## Architecture

- `rules.py` — small reusable normalization/validation functions
- `pipeline.py` — copy-on-write Pandas pipeline + `CleaningReport`
- `tests/` — schema, determinism, mutation-safety, and quality-rule tests
- `examples/` — synthetic input and runnable pipeline
- `.github/workflows/test.yml` — CI on every push/PR

## Decisions I can explain

The pipeline never mutates the caller's DataFrame, which makes notebook/debug behavior less surprising. Duplicate removal uses `customer_id` as the business key and preserves the first record; in a real system I would replace that simple rule with source priority or event timestamps. Invalid values become missing rather than being guessed, because silent correction can create believable but false data.

## Production direction

Add schema contracts with Pandera/Great Expectations, configurable rule sets, column-level lineage, Parquet/warehouse I/O, quality thresholds that fail a pipeline, orchestration, and validation of model features before training or inference.

## Scope

Synthetic data only. The rules are intentionally small enough to discuss line-by-line in an interview while still showing production-oriented data-quality thinking.
