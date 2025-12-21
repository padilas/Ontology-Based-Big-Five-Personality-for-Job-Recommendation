#!/usr/bin/env python3
"""Fix ont.: prefix to ont: in jobs_clean.ttl"""

print("Reading jobs_clean.ttl...")
with open('jobs_clean.ttl', 'r', encoding='utf-8') as f:
    content = f.read()

print("Replacing ont.: with ont:...")
fixed_content = content.replace('ont.:', 'ont:')

print("Writing back to jobs_clean.ttl...")
with open('jobs_clean.ttl', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ Done! Fixed all ont.: prefixes")
