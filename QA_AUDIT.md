# Final QA audit

- Raw agent output: 100 records, 100 unique IDs, 100 unique apps.
- Every record has exactly 3 web-evidence searches; no captured search call returned an error.
- Citation URLs are present in all 100 records.
- The original catalog classifier had a fuzzy-match bug: any search candidate was treated as coverage. This is fixed in `research_agent_v3.py`.
- Exact and related/variant catalog results are now separated.
- The final source bundle includes `apps.csv` and a functional extraction script.
- Verification is claim-level and sampled, not full 100-app verification.
- Current verification log: 39 checks; PASS=33, CORRECTED=1, UNRESOLVED=5.
- Google Ads developer-token wording is corrected for the 2026-09-09 sunset.

The 39-check figure must not be described as a 20-app verification sample: it covers 13 apps with 39 claim checks.
