# ☢ CVSS Armageddon

A deliberately silly, GeoCities-flavoured dashboard of every **CVSS ≥ 9.0** CVE published in the last 7 or 14 days, ranked by **blast radius**: roughly how many systems out there could be running the affected product.

Live page: GitHub Pages for this repo (Settings → Pages → Deploy from branch `main`, folder `/`).

## What's in it

- `index.html` – the whole page, no build step. Uses d3 v7 from cdnjs.
- `data/critical.json` – every CVE first published 6–19 Nov 2026 (UTC) whose highest CVSS base score is ≥ 9.0, with a normalised product group.
- `data/all_window.json` – every CVE published in the same window, with score, severity and publication time.
- `data/blast.json` – blast-radius tier per product group (1 = under ~1k deployments, 5 = millions). About 20 tiers are backed by a published install or exposure count (linked in the file); about 140 are order-of-magnitude estimates; the rest are unrated.
- `tools/` – the Python scripts that built the data from [CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5).

## Caveats

- Snapshot as of 19 Nov 2026, 22:01 UTC. It does not update itself.
- Scores are the highest CVSS in each record (CNA or CISA ADP) and mix CVSS 3.1 and 4.0.
- Blast radius measures how many systems might run a product, not how many are vulnerable. Many of these bugs need a specific configuration.
- Not a measure of exploitation. Check CISA KEV and the vendor advisory.
- The jokes are jokes. The scores are not.
