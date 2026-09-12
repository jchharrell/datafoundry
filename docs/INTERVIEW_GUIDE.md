# DataFoundry interview guide

## 30-second version

DataFoundry is a Pandas-based data-quality pipeline. It validates incoming rows against explicit contracts, quarantines bad records instead of silently deleting them, records row-level violation reasons, cleans accepted records deterministically, and emits a lineage receipt that fingerprints the input and output.

## Five-minute walkthrough

1. **Problem:** dirty data is unavoidable; silent cleaning makes bugs difficult to trace.
2. **`contracts.py`:** define required columns and validators as code.
3. **`quality_gate.py`:** return accepted rows, quarantined rows, structured violations, and a lineage receipt.
4. **`pipeline.py`:** perform deterministic normalization/deduplication only on accepted records.
5. **`cli.py`:** make the system usable outside a notebook; produce clean/quarantine/report artifacts.
6. **Tests:** assert not just cleaned values, but quarantine membership, violation reasons, fingerprints, and generated files.

## Questions I should be able to answer

### Why validate before cleaning?
Because some failures should not be silently repaired. A downstream contract defines what is acceptable. Cleaning can normalize known representations, but it should not invent a valid value when meaning is missing or wrong.

### Why preserve quarantined rows?
They are debugging evidence. If an upstream source starts emitting invalid values, the data team needs examples to identify the source, fix it, and potentially replay affected records.

### What is idempotency here?
If the same input is processed with the same logic, the accepted/cleaned result should be the same. The deterministic sorting, run ID, and fingerprints help make that property visible.

### Are the hashes security guarantees?
No. They are content fingerprints for reproducibility, not signatures or tamper-proof storage. A stronger production design could sign manifests or use an immutable catalog.

### What happens when the schema changes?
Production contracts should be versioned. A new field or rule should produce a new contract version so historical runs remain interpretable. Compatibility tests can verify whether a schema change is breaking.

### How would this scale beyond Pandas?
Keep the contract semantics and reporting format but execute them in Spark, Polars, SQL/dbt tests, or warehouse constraints. The core pattern—validate, quarantine, measure, lineage, replay—does not depend on Pandas.

### Why not just use Great Expectations or another library?
Those tools are useful. I built the small contract engine myself so I could understand and demonstrate the mechanics: row-level evidence, quarantine decisions, deterministic receipts, and how those pieces fit into an ETL handoff.

## Memorable angle

The line I would use in an interview is: **bad rows are evidence, not trash.** DataFoundry keeps enough information to answer “what was rejected, why, and which exact input produced this output?”

## What I would not claim

- The small contract engine replaces enterprise data-quality platforms.
- The SHA fingerprints make the pipeline cryptographically tamper-proof.
- The included state/email rules are universally correct business rules.
- Pandas is the right execution engine for every data volume.
