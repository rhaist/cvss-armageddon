import re
def clean_vendor(v):
    v=(v or '').strip()
    rep={'Oracle Corporation':'Oracle','SAP_SE':'SAP','Zohocorp':'Zoho','Apache Software Foundation':'Apache','Citrix NetScaler':'Citrix',
         'Hewlett Packard Enterprise (HPE)':'HPE','Axis Communications AB':'Axis','Eclipse Foundation':'Eclipse','Ubiquiti Inc':'Ubiquiti',
         'JTL-Software GmbH':'JTL','Comelit Group S.p.A.':'Comelit','PHP Group':'PHP','Wing FTP Software':'Wing FTP','Jacob N. Breetvelt':'',
         'Shenzhen Cudy Technology Co., Ltd.':'Cudy','Arista Networks':'Arista','Checkmk GmbH':'Checkmk','Dassault Systèmes':'Dassault'}
    if v in rep: return rep[v]
    return re.sub(r',? (Inc\.?|GmbH|Corporation|Corp\.|S\.p\.A\.|Co\., Ltd\.|Ltd\.?|AB|SIA)$','',v)
def group_of(r):
    v,p,cna=r['vendor'],r['product'],r['cna']
    if not v and cna=='CPANSec': return 'Perl CPAN modules','CPAN'
    V=clean_vendor(v)
    if V=='Microsoft':
        if p.startswith('Windows'): return 'Microsoft Windows',V
        if 'SharePoint' in p: return 'Microsoft SharePoint',V
        if 'SQL Server' in p: return 'Microsoft SQL Server',V
        if p.startswith('.NET'): return 'Microsoft .NET (ASP.NET Core)',V
    if V=='SAP' and re.search(r'NetWeaver|ABAP|Gateway|Web Dispatcher',p): return 'SAP NetWeaver / ABAP',V
    if V=='Citrix': return ('Citrix NetScaler Console' if p=='Console' else 'Citrix NetScaler ADC'),V
    if V=='Oracle' and 'Hyperion' in p: return 'Oracle Hyperion',V
    if V=='Oracle' and p in ('Oracle Application Object Library','Oracle Applications Framework','Oracle Universal Work Queue','Oracle Mobile Field Service'): return 'Oracle E-Business Suite',V
    if V in ('D-Link','Tenda','TOTOLINK','Linksys','TRENDnet','Edimax','Cudy','DrayTek','Zyxel'): return V+' routers & gateways',V
    if V=='Dell' and 'PowerStore' in p: return 'Dell PowerStore',V
    if V=='Fortinet': return (p if p.startswith('Forti') else 'Fortinet '+p),V
    if V in ('Unknown','','n/a') : return p,'WordPress plugin' if cna in ('WPScan','Wordfence','Patchstack') else (V or cna)
    if V=='revmakx': return 'WP Duplicate','revmakx'
    pl,vl=p.lower(),V.lower()
    if vl and (vl in pl): return p,V
    if V and V==V.lower() and ' ' not in V:
        return (p if pl==vl else f'{V}/{p}'),V
    return (f'{V} {p}' if V else p),V
