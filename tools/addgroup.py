import json,sys
sys.path.insert(0,'/home/claude')
from groups import group_of
f=sys.argv[1]; d=json.load(open(f))
for r in d['rows']: r['group']=group_of(r)[0]
d['meta'].append({"label":"groups.py","value":open('/home/claude/groups.py').read(),"type":"code","lang":"python"})
d['meta'].append({"label":"addgroup.py","value":open(__file__).read(),"type":"code","lang":"python"})
json.dump(d,open(f,'w'),ensure_ascii=False)
