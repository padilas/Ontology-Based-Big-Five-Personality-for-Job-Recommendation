#!/usr/bin/env python3
"""Convert jobs_clean_fixed.ttl to jobs.owl (RDF/XML format)"""

from rdflib import Graph

print("Loading jobs_clean_fixed.ttl...")
g = Graph()
g.parse("jobs_clean_fixed.ttl", format="turtle")
print(f"✓ Loaded {len(g)} triples")

print("\nSaving to jobs.owl (RDF/XML format)...")
g.serialize(destination="jobs.owl", format="xml")
print("✓ Done! jobs.owl created with classification rules")
