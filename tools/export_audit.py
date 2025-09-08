#!/usr/bin/env python3
import json, os, requests, sys, socket, argparse
BASE=os.path.dirname(os.path.dirname(__file__))
CONF=os.path.join(BASE,'config','auth.json')
AUDIT=os.path.join(BASE,'sessions','audit_signed.log')
cfg=json.load(open(CONF)) if os.path.exists(CONF) else {}
siem=cfg.get('siem',{})
parser=argparse.ArgumentParser(); parser.add_argument('--method',choices=['http','syslog'],default='http'); args=parser.parse_args()
if not os.path.exists(AUDIT): print('No audit file'); sys.exit(1)
data=open(AUDIT).read()
if args.method=='http' and siem.get('http_endpoint'):
    headers={'Authorization':'Bearer '+siem.get('http_token','')}
    r=requests.post(siem['http_endpoint'], data={'audit':data}, headers=headers, timeout=10)
    print('HTTP status', r.status_code)
elif args.method=='syslog':
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.sendto(data.encode(), ('localhost',514))
    print('sent to syslog localhost:514')
else:
    print('No endpoint configured')