#!/usr/bin/env python3
"""Rebuild data/critical.json and data/all_window.json from CVEProject/cvelistV5.

Usage (from the repo root):
    python3 tools/refresh.py [--days 14] [--work /tmp/cva]

Takes every CVE first published in the last N UTC days (today included), keeps the
highest CVSS base score in each record (CNA or ADP), and prints the product groups
with a CVSS >= 9.0 that have no blast-radius tier in data/blast.json yet.
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from groups import group_of  # noqa: E402

DELTA = 'https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/deltaLog.json'


def scores(container):
    out = []
    for m in container.get('metrics', []) or []:
        for k, v in m.items():
            if k.startswith('cvssV') and isinstance(v, dict) and 'baseScore' in v:
                out.append((float(v['baseScore']), k.replace('cvssV', '').replace('_', '.'), v.get('vectorString', '')))
    return out


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=14)
    ap.add_argument('--work', default='/tmp/cva')
    a = ap.parse_args()

    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=a.days - 1)
    recs = os.path.join(a.work, 'recs')
    os.makedirs(recs, exist_ok=True)

    delta_path = os.path.join(a.work, 'delta.json')
    subprocess.run(['curl', '-fsS', '-m', '120', '-o', delta_path, DELTA], check=True)
    delta = json.load(open(delta_path))
    links = {}
    cutoff = (start - dt.timedelta(days=1)).isoformat()
    for e in reversed(delta):  # oldest first, so later updates win
        if e.get('fetchTime', '') < cutoff:
            continue
        for n in (e.get('new') or []) + (e.get('updated') or []):
            links[n['cveId']] = n['githubLink']
    print(f'{len(links)} records to fetch for {start} .. {today}', file=sys.stderr)

    cmd = 'curl -fsS -m 30 -o "%s/$(basename "$0")" "$0" || true' % recs
    subprocess.run(['xargs', '-P', '32', '-n', '1', 'sh', '-c', cmd], input='\n'.join(links.values()), text=True, check=True)

    allrows, crit = [], []
    for f in sorted(glob.glob(os.path.join(recs, '*.json'))):
        try:
            r = json.load(open(f))
        except Exception:
            continue
        md = r.get('cveMetadata', {})
        pub = md.get('datePublished', '') or ''
        if md.get('state') != 'PUBLISHED' or not (start.isoformat() <= pub[:10] <= today.isoformat()):
            continue
        cna = r['containers'].get('cna', {})
        s = scores(cna)
        for adp in r['containers'].get('adp', []) or []:
            s += scores(adp)
        best = max(s) if s else None
        aff = (cna.get('affected') or [{}])[0]
        score = best[0] if best else None
        sev = ('unscored' if score is None else 'critical' if score >= 9 else 'high' if score >= 7
               else 'medium' if score >= 4 else 'low' if score > 0 else 'none')
        row = dict(id=md['cveId'], score=score, severity=sev, day=pub[:10], hour=int(pub[11:13] or 0),
                   published=pub[:19] + 'Z')
        allrows.append(row)
        if score is not None and score >= 9:
            vec = best[2]
            av = re.search(r'AV:([NALP])', vec)
            pr = re.search(r'PR:([NLH])', vec)
            cwe = []
            for pt in cna.get('problemTypes', []) or []:
                for d in pt.get('descriptions', []):
                    if d.get('cweId'):
                        cwe.append(d['cweId'])
            desc = clean(next((d['value'] for d in cna.get('descriptions', []) if d.get('lang', '').startswith('en')), ''))
            c = dict(id=row['id'], score=score, cvss=best[1], vector=vec,
                     attack_vector={'N': 'Network', 'A': 'Adjacent', 'L': 'Local', 'P': 'Physical'}.get(av.group(1) if av else '', '?'),
                     privileges={'N': 'None', 'L': 'Low', 'H': 'High'}.get(pr.group(1) if pr else '', '?'),
                     cna=md.get('assignerShortName', ''), vendor=clean(aff.get('vendor', '')), product=clean(aff.get('product', '')),
                     cwe=', '.join(dict.fromkeys(cwe)) or '—', summary=desc[:320] + ('…' if len(desc) > 320 else ''),
                     published=row['published'], url='https://www.cve.org/CVERecord?id=' + row['id'], day=row['day'])
            c['group'] = group_of(c)[0]
            crit.append(c)
    crit.sort(key=lambda c: (-c['score'], c['id']))

    snap = max((d.get('fetchTime', '') for d in delta), default='')
    meta = [{'label': 'refresh.py', 'value': open(__file__).read(), 'type': 'code', 'lang': 'python'},
            {'label': 'groups.py', 'value': open(os.path.join(HERE, 'groups.py')).read(), 'type': 'code', 'lang': 'python'},
            {'label': 'Input', 'value': f'CVEProject/cvelistV5 records first published {start} to {today} UTC (delta log fetched {snap})'}]
    json.dump({'rows': crit, 'meta': meta}, open(os.path.join(ROOT, 'data', 'critical.json'), 'w'), ensure_ascii=False)
    json.dump({'rows': allrows, 'meta': meta}, open(os.path.join(ROOT, 'data', 'all_window.json'), 'w'),
              ensure_ascii=False, separators=(',', ':'))

    blast = {b['group'] for b in json.load(open(os.path.join(ROOT, 'data', 'blast.json')))['rows']}
    groups = collections.defaultdict(list)
    for c in crit:
        if c['group'] not in blast:
            groups[c['group']].append(c)
    print(json.dumps({'window': [start.isoformat(), today.isoformat()], 'snapshot': snap, 'all': len(allrows),
                      'critical': len(crit), 'unrated_groups': len(groups)}))
    for g, cs in sorted(groups.items(), key=lambda kv: -max(c['score'] for c in kv[1])):
        top = max(cs, key=lambda c: c['score'])
        print(f"UNRATED\t{top['score']}\t{len(cs)}\t{top['cna']}\t{g}\t{top['summary'][:110]}")


if __name__ == '__main__':
    main()
