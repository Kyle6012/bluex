#!/usr/bin/env python3
"""Ingest audit file to Elasticsearch bulk API (assumes index exists).
Config: config/auth.json -> siem.elastic {'endpoint':'http://es:9200','index':'bluex-audit'}"""
import requests, json, os, sys
BASE=os.path.dirname(os.path.dirname(__file__))
CONF=os.path.join(BASE,'config','auth.json')
cfg=json.load(open(CONF)) if os.path.exists(CONF) else {}
es = cfg.get('siem',{}).get('elastic',{})
if not es.get('endpoint'):
    print('Configure elastic in config/auth.json'); sys.exit(1)
AUDIT=os.path.join(BASE,'sessions','audit_signed.log')
bulk=[]
with open(AUDIT) as f:
    for line in f:
        sig,payload=line.strip().split(' ',1)
        # action meta
        bulk.append(json.dumps({'index':{'_index':es.get('index','bluex-audit')}}))
        doc = json.loads(payload)
        doc['_signature']=sig
        bulk.append(json.dumps(doc))
body='\n'.join(bulk)+'\n'
resp = requests.post(es['endpoint']+'/_bulk', data=body, headers={'Content-Type':'application/x-ndjson'}, timeout=20)
print('status', resp.status_code, resp.text)
