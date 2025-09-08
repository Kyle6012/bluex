#!/usr/bin/env python3
"""Generate per-org report and email to org admins configured in config/auth.json -> orgs entries may include 'admin_email'.
Usage: tools/schedule_report.py ORG_CODE
"""
import os, sys, json, csv, smtplib, tempfile
from email.message import EmailMessage
BASE=os.path.dirname(os.path.dirname(__file__))
CONFIG=os.path.join(BASE,'config','auth.json')
ORGS=os.path.join(BASE,'config','orgs.json')
REPORTS=os.path.join(BASE,'reports')
if len(sys.argv)<2:
    print('Usage: schedule_report.py ORG_CODE'); sys.exit(1)
org_code = sys.argv[1]
orgs = json.load(open(ORGS)) if os.path.exists(ORGS) else []
org = next((o for o in orgs if o.get('code')==org_code), None)
if not org:
    print('Org not found'); sys.exit(2)
# gather rows
rows=[]
for p in os.listdir(os.path.join(REPORTS,'students')) if os.path.exists(os.path.join(REPORTS,'students')) else []:
    if org_code in p:
        rows.append({'type':'student_report','file':p})
for p in os.listdir(os.path.join(REPORTS,'practice_submissions')) if os.path.exists(os.path.join(REPORTS,'practice_submissions')) else []:
    if org_code in p:
        rows.append({'type':'practice','file':p})
# write csv to temp
fd, path = tempfile.mkstemp(suffix='_'+org_code+'_report.csv')
with os.fdopen(fd,'w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['type','file'])
    w.writeheader(); w.writerows(rows)
# send email if admin_email configured
cfg = json.load(open(CONFIG)) if os.path.exists(CONFIG) else {}
smtp = cfg.get('smtp',{})
admin = org.get('admin_email')
if admin and smtp.get('server'):
    msg = EmailMessage(); msg['Subject'] = f'Blue-X Report for {org.get("name")}'
    msg['From'] = smtp.get('from','bluex@example.com'); msg['To'] = admin
    msg.set_content('Attached is the scheduled report.')
    with open(path,'rb') as fh:
        data = fh.read()
    msg.add_attachment(data, maintype='text', subtype='csv', filename=os.path.basename(path))
    s = smtplib.SMTP(smtp['server'], smtp.get('port',25))
    if smtp.get('starttls'): s.starttls()
    if smtp.get('username'):
        s.login(smtp.get('username'), smtp.get('password'))
    s.send_message(msg); s.quit()
    print('Emailed to', admin)
else:
    print('No admin email or SMTP config; report saved to', path)
