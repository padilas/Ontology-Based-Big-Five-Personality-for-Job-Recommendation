from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph

from scripts.bigfive_scores import materialize_big_five_scores


@dataclass(frozen=True)
class RankedRow:
    app: str
    person: str
    job: str
    total_score: float


def load_query(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iri_to_str(node) -> str:
    return str(node)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ttl_path = root / "jobs.ttl"
    query_path = root / "queries" / "top10_applications.rq"

    g = Graph()

    # `jobs.ttl` contains a very large SWRL section (generated OWLAPI RDF lists)
    # that is expensive to parse and not needed for ranking.
    # We keep the ontology content before the "Rules" section and also keep the
    # optional sample-data block appended at the end of the file.
    ttl_text = ttl_path.read_text(encoding="utf-8")
    rules_marker = "#    Rules"
    sample_marker = "#    Sample data (for ranking pipeline demo)"

    rules_idx = ttl_text.find(rules_marker)
    sample_idx = ttl_text.find(sample_marker)
    if rules_idx != -1 and sample_idx != -1 and sample_idx > rules_idx:
        ttl_text = ttl_text[:rules_idx] + ttl_text[sample_idx:]
    elif rules_idx != -1:
        ttl_text = ttl_text[:rules_idx]

    g.parse(data=ttl_text, format="turtle")

    # Ensure Big Five scores exist even when SWRL rules are not executed.
    materialize_big_five_scores(g)

    q = load_query(query_path)
    rows = []
    for r in g.query(q):
        app = iri_to_str(r.app)
        person = iri_to_str(r.person)
        job = iri_to_str(r.job)
        total = float(r.totalScore)
        rows.append(RankedRow(app=app, person=person, job=job, total_score=total))

    if not rows:
        print("No :Application individuals found in jobs.ttl. Add application data first.")
        return

    rows.sort(key=lambda x: x.total_score, reverse=True)
    k = max(1, math.ceil(len(rows) * 0.10))

    print(f"Total applications: {len(rows)}")
    print(f"Top 10% count: {k}")
    print("---")
    for i, row in enumerate(rows[:k], start=1):
        print(f"{i:>3}. score={row.total_score:.4f}\n     app={row.app}\n     person={row.person}\n     job={row.job}")


if __name__ == "__main__":
    main()
