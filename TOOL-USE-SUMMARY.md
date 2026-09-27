# Tool-use summary

- **ChatGPT, GPT-5.6 Luna:** used for experiment structure, implementation assistance, documentation drafting and critical review. Outputs were checked by running the code, inspecting the generated CSV/JSON, and running the unit-test suite. A test expectation was corrected after the opt-out row was intentionally retained as an inspectable exclusion.
- **Python 3.10+ standard library:** used for deterministic CSV/JSON processing, timestamp calculations, rule evaluation, generated evidence, and unit tests. No paid API, credentials, or external service calls are used.
- **Official web documentation:** used to verify alternative-tool capabilities. Vendor claims were not treated as evidence of customer adoption or cost fit.

Concrete verification example: the raw event export contains 128 rows but only 124 unique event IDs. Counting all rows would report 412 known active minutes; deduplicating stable event IDs gives 400. The prototype uses the deduplicated figure.
