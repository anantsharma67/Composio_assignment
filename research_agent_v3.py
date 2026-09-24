"""Composio Product Ops Research Agent v3.

Catalog-first, but uses per-app toolkit search instead of loading the entire catalog.
Prints progress so the run is observable. Web evidence is stored as raw tool output;
verification remains a separate human QA step.
"""
import os, json, re, time
from pathlib import Path
import pandas as pd
from composio import Composio

SEARCH_TOOL = "COMPOSIO_SEARCH_WEB"


def normalize(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def toolkit_to_dict(t):
    if isinstance(t, dict):
        return t
    out = {}
    for k in ("name", "slug", "auth_schemes", "composio_managed_auth_schemes", "no_auth", "meta"):
        if hasattr(t, k):
            out[k] = getattr(t, k)
    return out


def find_toolkit(composio, app_name):
    """Search the Composio toolkit catalog for one app."""
    try:
        resp = composio.toolkits.get(query={"search": app_name, "limit": 20})
        if isinstance(resp, dict):
            items = resp.get("items") or resp.get("data") or []
        else:
            items = resp or []
        candidates = [toolkit_to_dict(x) for x in items]
        target = normalize(app_name)
        exact = []
        related = []
        for t in candidates:
            name = normalize(t.get("name", ""))
            slug = normalize(t.get("slug", ""))
            if target == name or target == slug:
                exact.append(t)
            else:
                related.append(t)
        return {"exact": exact, "related": related[:5]}
    except Exception as e:
        return {"exact": [], "related": [], "error": repr(e)}


def search_queries(app):
    return [
        f'"{app}" official developer documentation API authentication OAuth API key',
        f'"{app}" official developer documentation credentials API access pricing approval partner',
        f'"{app}" official MCP server Model Context Protocol developer',
    ]


def collect_web_evidence(session, app):
    results = []
    for i, q in enumerate(search_queries(app), 1):
        print(f"    web search {i}/3...", flush=True)
        try:
            r = session.execute(SEARCH_TOOL, arguments={"query": q})
            results.append({"query": q, "result": r})
        except Exception as e:
            results.append({"query": q, "error": repr(e)})
    return results


def main():
    apps_path = os.getenv("APPS_CSV", "apps.csv")
    out_path = os.getenv("OUT_CSV", "agent_output.jsonl")
    apps = pd.read_csv(apps_path)

    if "id" not in apps.columns or "app" not in apps.columns:
        raise ValueError("apps.csv must contain 'id' and 'app' columns")

    api_key = os.environ.get("COMPOSIO_API_KEY")
    if not api_key:
        raise RuntimeError("COMPOSIO_API_KEY is not set")

    composio = Composio(api_key=api_key)
    print(f"Loaded {len(apps)} apps.", flush=True)
    print("Creating Composio session...", flush=True)
    session = composio.sessions.create(
        user_id=os.getenv("COMPOSIO_USER_ID", "composio-researcher")
    )
    print(f"Session OK: {session.session_id}", flush=True)

    mode = os.getenv("RESEARCH_MODE", "all").lower()
    with open(out_path, "w", encoding="utf-8") as f:
        for idx, (_, row) in enumerate(apps.iterrows(), 1):
            app_name = str(row["app"])
            print(f"\n[{idx}/{len(apps)}] {app_name}", flush=True)
            catalog = find_toolkit(composio, app_name)
            exact = catalog.get("exact", []) if isinstance(catalog, dict) else []
            related = catalog.get("related", []) if isinstance(catalog, dict) else []
            catalog_error = catalog.get("error") if isinstance(catalog, dict) else None
            covered = bool(exact)
            print(f"  Composio catalog: {'EXACT MATCH' if covered else ('RELATED RESULTS' if related else 'NO MATCH')}", flush=True)

            record = {
                "id": int(row["id"]),
                "app": app_name,
                "catalog_exact_matches": exact,
                "catalog_related_matches": related,
                "catalog_status": "exact_match" if covered else ("related_results" if related else ("error" if catalog_error else "not_found")),
                "catalog_error": catalog_error,
                "web_evidence": [],
            }

            # For the assignment we want comparable evidence across all apps.
            # Set RESEARCH_MODE=catalog_only to skip web searches during a dry run.
            if mode != "catalog_only":
                record["web_evidence"] = collect_web_evidence(session, app_name)

            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            print("  saved", flush=True)
            time.sleep(0.1)

    print(f"\nDONE — wrote {out_path} for {len(apps)} apps.", flush=True)


if __name__ == "__main__":
    main()
