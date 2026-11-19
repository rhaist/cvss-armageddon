import json,sys
sys.path.insert(0,'/home/claude')
code=open(__file__).read()
# tier: 5 = millions+, 4 = ~100k-1M, 3 = ~10k-100k, 2 = ~1k-10k, 1 = <1k deployments (order of magnitude); 0 = not rated
old={r['vendor']+'|'+r['product']:r for r in json.load(open('/home/claude/out/blast.json'))['rows']}
from groups import group_of
G=lambda v,p,cna='': group_of(dict(vendor=v,product=p,cna=cna))[0]
rows={}
for k,r in old.items():
    g=G(r['vendor'],r['product'],'WPScan' if r['vendor']=='revmakx' else '')
    rows[g]=dict(group=g,name=r['name'],tier=r['tier'],reach=r['reach'],basis=r['basis'],source=r['source'],confidence=r['confidence'],label='')
EST='Order-of-magnitude estimate from the product\'s market position; no published count checked.'
def add(g,tier,reach,basis=EST,name=None,label=''):
    rows[g]=dict(group=g,name=name or g,tier=tier,reach=reach,basis=basis,source='',confidence='estimated',label=label)
CLOUD='Cloud service: the vendor fixed it on its side, usually with nothing for customers to patch.'
for g in ['Microsoft Entra Device Registration','Microsoft Azure Managed Grafana','Microsoft Azure Open AI','Microsoft Azure Privileged Identity Management (PIM)','Jet Admin Cloud Platform','Adobe Experience Manager as a Cloud Service']:
    add(g,0,'Cloud service, already patched by the vendor',CLOUD,label='VENDOR-FIXED CLOUD')
T5=[('Microsoft Windows','Over a billion PCs and servers','Several of these are in components that are off by default (DHCP Server, iSCSI); check which roles you run.'),
    ('Google Chrome','Billions of browser installs, plus every Chromium-based browser',None),
    ('Google Android','Billions of active devices; patch speed depends on each phone maker',None),
    ('Mozilla Firefox','Hundreds of millions of users',None),
    ('Linux','Billions of devices; each bug sits in one kernel subsystem','Exposure depends on whether the affected subsystem is built and loaded.'),
    ('react','Millions of sites and apps','Check which React package and rendering mode the CVE names before you panic.'),
    ('Contact Form 7','About 5 million active WordPress installs',None),
    ('Microsoft Visual Studio Code','Tens of millions of developers',None),
    ('Zoom Communications Zoom Workplace','Hundreds of millions of users',None),
    ('Oracle MySQL Server','Millions of databases',None),
    ('F5 NGINX Open Source','Roughly a third of the web\'s servers','Usually only specific modules or configurations are affected.')]
for g,r,b in T5: add(g,5,r,b or EST,name={'react':'React','Zoom Communications Zoom Workplace':'Zoom Workplace','F5 NGINX Open Source':'NGINX (open source)'}.get(g))
T4=[('Microsoft SharePoint','Large on-prem enterprise footprint'),('Microsoft SQL Server','Huge enterprise database footprint'),('Microsoft .NET (ASP.NET Core)','Very large app footprint'),
    ('Oracle Database Server','Most large enterprises'),('Oracle WebLogic Server','Large enterprise footprint, often internet-facing'),('SAP NetWeaver / ABAP','Most SAP customers run ABAP systems'),
    ('FortiOS','Hundreds of thousands of FortiGate firewalls'),('Citrix NetScaler ADC','Tens of thousands internet-facing remote-access gateways'),('F5 BIG-IP','Tens of thousands of load balancers and gateways'),
    ('HPE ArubaOS (AOS)','Large campus Wi-Fi footprint'),('Synology DiskStation Manager (DSM)','Millions of NAS boxes in homes and small businesses'),('Apache Shiro','Embedded in many Java apps'),
    ('MongoDB Server','Very large database footprint'),('MongoDB Node.js Driver','Millions of weekly npm downloads'),('Automattic mongoose','Millions of weekly npm downloads'),
    ('Go toolchain cmd/go','Every Go developer and build pipeline'),('Perl CPAN modules','JSON::XS and friends sit under a lot of Perl'),('Apache Commons Codec','Dependency of a large share of Java apps'),
    ('cyrusimap/cyrus-sasl','Shipped in most Linux distributions'),('D-Link routers & gateways','Millions of consumer devices, many end-of-life'),('Tenda routers & gateways','Millions of consumer routers'),
    ('Linksys routers & gateways','Millions of consumer routers'),('pi-hole/FTL','Hundreds of thousands of home networks'),('Google Chrome OS','')]
for g,r in T4:
    if r: add(g,4,r,name={'Synology DiskStation Manager (DSM)':'Synology DSM','pi-hole/FTL':'Pi-hole FTL','Automattic mongoose':'Mongoose','cyrusimap/cyrus-sasl':'Cyrus SASL','Go toolchain cmd/go':'Go toolchain (cmd/go)','HPE ArubaOS (AOS)':'HPE ArubaOS'}.get(g))
T3=['IBM API Connect','Apache TomEE','Oracle Hyperion','Oracle E-Business Suite','Oracle PeopleSoft Enterprise PeopleTools','Oracle APEX','Oracle Access Manager','Oracle Business Intelligence Enterprise Edition',
    'Oracle REST Data Services','Oracle Service Bus','Oracle Platform Security for Java','Oracle Application Development Framework (ADF)','Adobe Experience Manager 6.5','Arista EOS','FortiMail','FortiManager','FortiAnalyzer',
    'FortiClientMac','N-able N-central','Checkmk','Apache Airflow','Kiteworks ownCloud','SmarterTools SmarterMail','Control Web Panel','mailcow: dockerized','arendst/Tasmota','Eclipse Mosquitto','TopThink ThinkPHP',
    'craftcms/cms','openemr','TOTOLINK routers & gateways','DrayTek routers & gateways','TRENDnet routers & gateways','Zyxel routers & gateways','F5 NGINX Plus','Microsoft Azure DevOps','JetBrains CLion','IBM Aspera Faspex',
    'PTC Windchill','Siemens Mendix Studio Pro 11','Versa VOS','Red Hat Satellite 6.16 for RHEL 8','Red Hat Build of Keycloak','Apache Axis2/Java','Apache Axis 1.x (EOL)','Apache XML Graphics FOP','civetweb','alanxz/rabbitmq-c',
    'signalwire/freeswitch','directus','kyverno','AXIS Camera Station Pro','Weaver Network E-cology','Baidu UEditor','SAP S4CRM','SAP BusinessObjects Business Intelligence Platform (Web Intelligence)','TYPO3 CMS','ivanti/Endpoint Manager',
    'pnpm/exe','OpenIdentityPlatform OpenAM','Broadcom AutoSys Workload Automation','Oracle Database Server']
NOTE3={'N-able N-central':'MSP tool: one server manages many customer networks, so one hit fans out.','TYPO3 CMS':'Especially common in Germany, Austria and Switzerland.','DrayTek routers & gateways':'Popular SMB gateways in the UK and EU.'}
for g in T3:
    if g not in rows: add(g,3,'Roughly tens of thousands of deployments',NOTE3.get(g,EST),name={'craftcms/cms':'Craft CMS','openemr':'OpenEMR','arendst/Tasmota':'Tasmota','ivanti/Endpoint Manager':'Ivanti Endpoint Manager','pnpm/exe':'pnpm (standalone exe)','alanxz/rabbitmq-c':'rabbitmq-c','signalwire/freeswitch':'FreeSWITCH','mailcow: dockerized':'mailcow','TopThink ThinkPHP':'ThinkPHP','Siemens Mendix Studio Pro 11':'Siemens Mendix Studio Pro','Red Hat Satellite 6.16 for RHEL 8':'Red Hat Satellite'}.get(g))
T2=['Adobe Connect','Oracle AutoVue','Arista Wi-Fi Access Point','FortiAuthenticator','Citrix NetScaler Console','AmidaWare Tactical RMM','WebPros Plesk extension "Site Import"','OpenMage magento-lts','getgrav/grav','Copeland XWEB EVO',
    'lxc/incus','nocodb','siyuan-note/siyuan','dokploy','Microsoft GDK','Microsoft Aspire Dashboard','JetBrains Hub','JetBrains Datalore','Zoho DDI Central','Zoho M365 Manager Plus','Zoho AssetExplorer','Hitachi HiRDB Server Version 10',
    'Red Hat OpenShift AI (RHOAI)','Apache Axis2/C','Apache James','Lucee Server','Traccar','Seafile SeaDoc','Kozea Radicale','zoneminder','OpenCTI-Platform opencti','misp-modules','GeoVision GV-Face','Enter Iperius Backup',
    'Devolutions Agent','Airlock by Ergon Airlock Gateway','Ivanti Cloud Services Application','Edimax routers & gateways','Cudy routers & gateways','Microsoft Azure DevOps']
for g in T2:
    if g not in rows: add(g,2,'Roughly low thousands of deployments',name={'OpenCTI-Platform opencti':'OpenCTI','lxc/incus':'Incus','siyuan-note/siyuan':'SiYuan','nocodb':'NocoDB','dokploy':'Dokploy','zoneminder':'ZoneMinder','getgrav/grav':'Grav CMS'}.get(g))
LATE=[('OpenSSL',5,'In most servers, operating systems and appliances','EVP_EncodeBlock needs an input close to INT_MAX, and the QUIC bug only matters if you use OpenSSL QUIC, so real exposure is far smaller.','OpenSSL'),
 ('nltk',4,'Millions of monthly pip installs',EST,'NLTK'),
 ('MongoDB Java Driver',4,'Very large Java app footprint','Only affects connections using a DNS seedlist (mongodb+srv) URI.',None),
 ('Splunk Enterprise',4,'Large enterprise SIEM footprint','Two of these are pre-authentication; check which Splunk version you run.',None),
 ('Splunk Enterprise Security',3,'Roughly tens of thousands of deployments',EST,None),
 ('Splunk SOAR',3,'Roughly tens of thousands of deployments',EST,None),
 ('MongoDB C# Driver',3,'Roughly tens of thousands of apps','Only affects connections using a DNS SRV connection string.',None),
 ('IBM Guardium Data Protection',3,'Roughly tens of thousands of deployments',EST,None),
 ('WatchGuard Dimension',3,'Roughly tens of thousands of deployments',EST,None),
 ('etherpad',3,'Roughly tens of thousands of deployments',EST,'Etherpad'),
 ('Apache SeaTunnel Web',2,'Roughly low thousands of deployments','Marked unsupported when assigned: there may be no fix coming.',None),
 ('Autonomy Logic OpenPLC Runtime',2,'Roughly low thousands of deployments','Industrial control runtime; mostly labs and small installs.','OpenPLC Runtime'),
 ('fabiolb/fabio',2,'Roughly low thousands of deployments',EST,'Fabio'),
 ('Apache Iggy',1,'Under ~1,000 deployments',EST,None),
 ('Apache Iggy Go SDK',1,'Under ~1,000 deployments',EST,None),
 ('lbr38/repomanager',1,'Under ~1,000 deployments',EST,'RepoManager'),
 ('flytohub/flyto-core',1,'Under ~1,000 deployments',EST,'Flyto Core')]
for g,t,r,b,n in LATE: add(g,t,r,b,name=n)
for g in ['Apache Roller','Apache Allura','n/a/Intel(R) TDX Migration Trust Domain (MigTD)','Intel(R) TDX Migration Trust Domain (MigTD)']:
    add(g,1,'Under ~1,000 deployments')
out=sorted(rows.values(),key=lambda r:(-r['tier'],r['group']))
meta=[{"label":"blast2.py","value":code,"type":"code","lang":"python"},{"label":"groups.py","value":open('/home/claude/groups.py').read(),"type":"code","lang":"python"},
      {"label":"Input","value":"Earlier blast.json (public counts found by web search on 19 Nov 2026) plus order-of-magnitude estimates for well-known products; everything else is left not rated"}]
json.dump({"rows":out,"meta":meta},open(sys.argv[1],'w'),ensure_ascii=False)
c=json.load(open(sys.argv[2] if len(sys.argv)>2 else '/home/claude/out/critical.json'))['rows']
gs={group_of(r)[0] for r in c}
print('rated groups present',len([g for g in gs if g in rows]),'of',len(gs)); print('unused rules',[g for g in rows if g not in gs])
