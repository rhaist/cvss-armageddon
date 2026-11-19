import json,sys
f=sys.argv[1]; d=json.load(open(f))
d['rows']=[{k:r[k] for k in ('id','score','severity','day','hour','published')} for r in d['rows']]
d['meta'].append({"label":"slim.py","value":open(__file__).read(),"type":"code","lang":"python"})
json.dump(d,open(f,'w'),ensure_ascii=False,separators=(',',':'))
