"""Convert agent_output.jsonl into a reviewable first-pass CSV.

Works with research_agent_v3.py output. Exact and related catalog results
remain separate so fuzzy search results are never mislabeled as coverage.
"""
import json, re, pandas as pd, sys

def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())

def urls(x):
    return list(dict.fromkeys(re.findall(r"'url':\s*'([^']+)'", str(x))))

def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "agent_output.jsonl"
    out = sys.argv[2] if len(sys.argv) > 2 else "structured_research_first_pass.csv"
    apps = pd.read_csv("apps.csv").set_index("id")
    rows = []

    with open(inp, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            exact = r.get("catalog_exact_matches", [])
            related = r.get("catalog_related_matches", [])

            # Backward compatibility with the original captured v2 output.
            if not exact and not related and "catalog_matches" in r:
                target = norm(r["app"])
                for m in r.get("catalog_matches", []) or []:
                    if "error" in m:
                        continue
                    if target == norm(m.get("name", "")) or target == norm(m.get("slug", "")):
                        exact.append(m)
                    else:
                        related.append(m)

            evidence_urls = []
            auth_urls = []
            credential_urls = []
            mcp_urls = []

            for e in r.get("web_evidence", []):
                u = urls(e.get("result", ""))
                evidence_urls.extend(u)
                q = e.get("query", "").lower()
                if "authentication" in q:
                    auth_urls = u
                elif "credentials" in q or "pricing" in q:
                    credential_urls = u
                elif "mcp" in q:
                    mcp_urls = u

            if exact:
                coverage = "Exact toolkit match"
            elif related:
                coverage = "Related/variant catalog match — scope needs verification"
            else:
                coverage = "No exact catalog match found"

            rows.append({
                "ID": r["id"],
                "App": r["app"],
                "Category": apps.loc[r["id"], "category"],
                "One-line description (working)": apps.loc[r["id"], "description_hint"],
                "Composio coverage": coverage,
                "Exact toolkit name": "; ".join(m.get("name", "") for m in exact),
                "Related catalog results": "; ".join(m.get("name", "") for m in related),
                "Evidence URLs": " | ".join(dict.fromkeys(evidence_urls)),
                "Auth evidence": " | ".join(auth_urls),
                "Credential evidence": " | ".join(credential_urls),
                "MCP evidence": " | ".join(mcp_urls),
                "Verification status": "Pending — first-pass agent result; only sampled claims are manually verified"
            })

    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Wrote {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
