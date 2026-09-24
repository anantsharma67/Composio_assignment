# Composio Product Ops — 100-App Integration Readiness

## What this repository contains
A catalog-first research agent and human-verification workflow for the Composio AI Product Ops take-home.

## Pipeline
1. `apps.csv` — clean 100-app input.
2. `research_agent_v3.py` — Composio catalog lookup + three web research queries per app.
3. `agent_output.jsonl` — raw output from the captured v2 run.
4. `agent_output_reclassified.jsonl` — same run reclassified with exact-vs-related catalog matching.
5. `extract_structured_v2.py` — deterministic evidence/CSV extraction.
6. `structured_research_first_pass_v3.csv` — corrected first-pass matrix.
7. `verification_log_v2.csv` — claim-level human QA.
8. `structured_research_verified_v2.csv` — verification-aware matrix.
9. `verify.py` — creates a reviewer template; it does not fake verification.
10. `QA_AUDIT.md` — internal consistency and methodology audit.
11. `composio_product_ops_case_study_final_v2.html` — reviewer-facing single-page submission.

## Run
```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate

pip install composio pandas

# Set your Composio Project API key
# Windows PowerShell:
$env:COMPOSIO_API_KEY="..."

python research_agent_v3.py
python extract_structured_v2.py agent_output.jsonl structured_research_first_pass.csv
python verify.py agent_output.jsonl
```

## What changed during QA
The first agent implementation classified any fuzzy toolkit search result as a Composio match. That produced false positives such as Podio→Procfu and Front→Starton/Vercel. The final agent requires an exact normalized name/slug match for an “Exact toolkit match” and retains fuzzy results separately.

The corrected first-pass classification is:
- 57 exact toolkit matches
- 14 related/variant catalog results requiring scope verification
- 29 no exact catalog match

## Verification
The verification log contains 39 claim checks across 13 apps:
- 33 PASS
- 1 CORRECTED
- 5 UNRESOLVED

The sample is not presented as 100-app full verification. The one concrete correction is Google Ads: Google's current documentation says developer tokens were sunset on September 9, 2026 and are now optional/ignored by API servers.

## Honesty
A URL being reachable is not the same as a claim being verified. Unresolved claims remain unresolved. Community MCP implementations are not treated as official vendor MCP support.
