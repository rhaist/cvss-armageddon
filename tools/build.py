import json,glob,sys,re,os
src=sys.argv[1]; outdir=sys.argv[2]
code=open(__file__).read()
def scores(c):
    res=[]
    for m in c.get('metrics',[]) or []:
        for k,v in m.items():
            if k.startswith('cvssV') and isinstance(v,dict) and 'baseScore' in v:
                res.append((float(v['baseScore']),k.replace('cvssV','').replace('_','.'),v.get('vectorString','')))
    return res
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
allrows=[];crit=[];notToday=0
for f in sorted(glob.glob(src+'/*.json')):
    r=json.load(open(f)); md=r['cveMetadata']
    if md.get('state')!='PUBLISHED': continue
    pub=md.get('datePublished','')
    if not ('2026-11-06' <= pub[:10] <= '2026-11-19'): notToday+=1; continue
    cna=r['containers']['cna']
    s=scores(cna)
    for a in r['containers'].get('adp',[]) or []: s+=scores(a)
    best=max(s) if s else None
    aff=(cna.get('affected') or [{}])[0]
    score=best[0] if best else None
    sev='unscored' if score is None else 'critical' if score>=9 else 'high' if score>=7 else 'medium' if score>=4 else 'low' if score>0 else 'none'
    row=dict(id=md['cveId'],score=score,severity=sev,cna=md.get('assignerShortName',''),
             vendor=clean(aff.get('vendor','')),product=clean(aff.get('product','')),
             published=pub[:19]+'Z',day=pub[:10],hour=int(pub[11:13]))
    allrows.append(row)
    if score is not None and score>=9:
        vec=best[2]; av=re.search(r'AV:([NALP])',vec); pr=re.search(r'PR:([NLH])',vec)
        cwe=[]
        for pt in cna.get('problemTypes',[]) or []:
            for d in pt.get('descriptions',[]):
                if d.get('cweId'): cwe.append(d['cweId'])
        desc=clean(next((d['value'] for d in cna.get('descriptions',[]) if d.get('lang','').startswith('en')),''))
        crit.append(dict(id=row['id'],score=score,cvss=best[1],vector=vec,
            attack_vector={'N':'Network','A':'Adjacent','L':'Local','P':'Physical'}.get(av.group(1) if av else '', '?'),
            privileges={'N':'None','L':'Low','H':'High'}.get(pr.group(1) if pr else '', '?'),
            cna=row['cna'],vendor=row['vendor'],product=row['product'],cwe=', '.join(dict.fromkeys(cwe)) or '—',
            summary=desc[:320]+('…' if len(desc)>320 else ''),published=row['published'],
            url='https://www.cve.org/CVERecord?id='+row['id'],day=row['day']))
crit.sort(key=lambda c:(-c['score'],c['id']))
meta=[{"label":"build.py","value":code,"type":"code","lang":"python"},
      {"label":"Input","value":"CVEProject/cvelistV5 records listed as new in cves/deltaLog.json, first published 6-19 Nov 2026 UTC (snapshot 17:38 UTC on 19 Nov)"}]
json.dump({"rows":crit,"meta":meta},open(outdir+'/critical.json','w'),ensure_ascii=False)
json.dump({"rows":allrows,"meta":meta},open(outdir+'/all_window.json','w'),ensure_ascii=False)
print('not today',notToday,'all',len(allrows),'crit',len(crit))
