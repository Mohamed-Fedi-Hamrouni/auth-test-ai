# AI-assisted testing

This component will complement deterministic Robot Framework results. It will:

- parse Robot Framework `output.xml` files;
- redact and anonymize sensitive test data before any external processing;
- classify failures without changing the original Robot test result;
- generate a separate, human-reviewed analysis report.

External model calls and API credentials are intentionally absent. External AI
calls must remain disabled in CI by default.

