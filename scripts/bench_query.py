from __future__ import annotations

import time
from pathlib import Path

from rdflib import Graph

from scripts.bigfive_scores import materialize_big_five_scores


def load_jobs_graph(root: Path) -> Graph:
    ttl_path = root / "jobs.ttl"
    ttl_text = ttl_path.read_text(encoding="utf-8")

    rules_marker = "#    Rules"
    sample_marker = "#    Sample data (for ranking pipeline demo)"
    rules_idx = ttl_text.find(rules_marker)
    sample_idx = ttl_text.find(sample_marker)

    if rules_idx != -1 and sample_idx != -1 and sample_idx > rules_idx:
        ttl_text = ttl_text[:rules_idx] + ttl_text[sample_idx:]
    elif rules_idx != -1:
        ttl_text = ttl_text[:rules_idx]

    g = Graph()
    g.parse(data=ttl_text, format="turtle")

    # Ensure Big Five scores exist even when SWRL rules are not executed.
    materialize_big_five_scores(g)
    return g


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    query_path = root / "queries" / "top10_applications.rq"
    q = query_path.read_text(encoding="utf-8")

    print("Building graph...", flush=True)
    start = time.time()
    g = load_jobs_graph(root)
    print(f"Graph ready: {len(g)} triples in {time.time() - start:.2f}s", flush=True)

    print("Running query...", flush=True)
    start = time.time()
    results = list(g.query(q))
    print(f"Query returned {len(results)} rows in {time.time() - start:.2f}s", flush=True)

    for r in results[:5]:
        print(r, flush=True)


if __name__ == "__main__":
    main()
