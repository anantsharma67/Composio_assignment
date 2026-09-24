"""
Evidence verifier.

Input: agent_output.jsonl
Output: verification_results.csv

Important distinction:
- URL reachable != claim verified.
- A claim is "verified" only when a reviewer records the exact official
  source and the specific claim supported by that source.
- Automated checks flag suspicious/unsupported evidence; they do not
  manufacture accuracy percentages.

Recommended QA sample:
  * random sample
  * every "blocked" row
  * every low-confidence row
  * every MCP claim
  * finance/payment APIs
  * apps with partner/app-review gates
"""

import csv, json, re
from pathlib import Path

FIELDS = [
    "id","app","field","agent_value","source_url",
    "source_support","result","reviewer_note"
]

def classify(source_support):
    s=source_support.strip().lower()
    if s in {"yes","partial","no","unresolved"}:
        return s
    raise ValueError("source_support must be yes/partial/no/unresolved")

def write_review_template(agent_jsonl, out_csv="verification_results.csv"):
    rows=[]
    with open(agent_jsonl,encoding="utf-8") as f:
        for line in f:
            x=json.loads(line)
            # The reviewer fills these fields after reading the actual source.
            for field in ["auth","credential_path","api_surface","mcp","verdict"]:
                rows.append({
                    "id":x["id"],"app":x["app"],"field":field,
                    "agent_value":"",
                    "source_url":"",
                    "source_support":"",
                    "result":"pending",
                    "reviewer_note":"Read the official source and record whether it supports the exact claim."
                })
    with open(out_csv,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

if __name__=="__main__":
    import sys
    write_review_template(sys.argv[1] if len(sys.argv)>1 else "agent_output.jsonl")
