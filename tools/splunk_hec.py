#!/usr/bin/env python3
"""Send audit file to Splunk HTTP Event Collector (HEC)."""
import requests, json, os, sys
BASE=os.path.dirname(os.path.dirname(__file__))
CONF=os.path.join(BASE,'config','auth.json')
cfg=json.load(open(CONF)) if os.path.exists(CONF) else {}
hec = cfg.get('siem',{}).get('splunk_hec',{})
if not hec.get('endpoint'):
    print('Configure splunk_hec in config/auth.json')
    sys.exit(1)
AUDIT=os.path.join(BASE,'sessions','audit_signed.log')
with open(AUDIT) as f:
    for line in f:
        sig,payload=line.strip().split(' ',1)
        ev={'time':json.loads(payload).get('ts'),'host':'bluex','sourcetype':'bluex:audit','event':payload,'signature':sig}
        r=requests.post(hec['endpoint']+'/services/collector/event', headers={'Authorization':'Splunk '+hec.get('token')}, json=ev, timeout=10)
        print('sent', r.status_code)
