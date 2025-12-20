from __future__ import annotations

import time
from pathlib import Path

from rdflib import Graph


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ttl_path = root / "jobs.ttl"

    print("Reading...", flush=True)
    start = time.time()
    ttl_text = ttl_path.read_text(encoding="utf-8")
    print(f"Read {len(ttl_text)} bytes in {time.time() - start:.2f}s", flush=True)

    rules_marker = "#    Rules"
    sample_marker = "#    Sample data (for ranking pipeline demo)"
    rules_idx = ttl_text.find(rules_marker)
    sample_idx = ttl_text.find(sample_marker)
    print(f"rules_idx={rules_idx} sample_idx={sample_idx}", flush=True)

    if rules_idx != -1 and sample_idx != -1 and sample_idx > rules_idx:
        ttl_text = ttl_text[:rules_idx] + ttl_text[sample_idx:]
    elif rules_idx != -1:
        ttl_text = ttl_text[:rules_idx]

    print("Parsing...", flush=True)
    start = time.time()
    g = Graph()
    g.parse(data=ttl_text, format="turtle")
    print(f"Parsed {len(g)} triples in {time.time() - start:.2f}s", flush=True)


if __name__ == "__main__":
    main()
