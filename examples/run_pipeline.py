import json
import pandas as pd
from datafoundry import CleaningPipeline

raw = pd.read_csv("examples/customers_dirty.csv")
cleaned, report = CleaningPipeline().clean(raw)
cleaned.to_csv("examples/customers_clean.csv", index=False)
print(cleaned.to_string(index=False))
print(json.dumps(report.to_dict(), indent=2))
