#!/usr/bin/env python3
"""Convert jobs_clean.ttl to jobs.owl (RDF/XML format)"""

from rdflib import Graph

print("Loading jobs_clean.ttl...")
g = Graph()
g.parse("jobs_clean.ttl", format="turtle")
print(f"✓ Loaded {len(g)} triples")

print("\nSaving to jobs.owl (RDF/XML format)...")
g.serialize(destination="jobs.owl", format="xml")
print("✓ Done! jobs.owl created with classification rules")
