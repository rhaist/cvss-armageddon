#!/usr/bin/env python3
"""Merge blast-radius tiers into data/blast.json.

Usage (from the repo root):
    python3 tools/add_tiers.py new_tiers.json

new_tiers.json is a list of objects:
    {"group": "<exact group name from refresh.py>", "name": "<display name, optional>",
     "tier": 1-5 (0 with a label for vendor-fixed cloud services),
     "reach": "<short phrase>", "basis": "<one sentence>", "source": "<URL or empty>",
     "confidence": "measured" | "estimated", "label": "<optional, e.g. VENDOR-FIXED CLOUD>"}

Tier scale (order of magnitude of deployments): 1 under ~1k, 2 ~1k-10k, 3 ~10k-100k,
4 ~100k-1M, 5 millions. A row with confidence "measured" is never overwritten by an
"estimated" one.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, 'data', 'blast.json')
doc = json.load(open(path))
rows = {r['group']: r for r in doc['rows']}
added, kept = 0, 0
for n in json.load(open(sys.argv[1])):
    n = {'name': n.get('name') or n['group'], 'label': '', 'source': '', **n}
    if not isinstance(n.get('tier'), int) or not 0 <= n['tier'] <= 5:
        sys.exit(f"bad tier for {n['group']}: {n.get('tier')}")
    old = rows.get(n['group'])
    if old and old.get('confidence') == 'measured' and n.get('confidence') != 'measured':
        kept += 1
        continue
    rows[n['group']] = {k: n.get(k, '') for k in ('group', 'name', 'tier', 'reach', 'basis', 'source', 'confidence', 'label')}
    added += 1
doc['rows'] = sorted(rows.values(), key=lambda r: (-r['tier'], r['group']))
json.dump(doc, open(path, 'w'), ensure_ascii=False)
print(f'{added} tiers written, {kept} measured tiers kept, {len(doc["rows"])} total')
