#!/usr/bin/env python3
"""Manage instructor credentials for Blue-X Attack Mode lock (stores salted SHA256)."""
import os, sys, hashlib, getpass, json
BASE=os.path.dirname(os.path.dirname(__file__))
CONF=os.path.join(BASE,'config','instructor.json')
os.makedirs(os.path.dirname(CONF), exist_ok=True)
def set_password():
    p1=getpass.getpass('Enter new instructor password: ')
    p2=getpass.getpass('Confirm password: ')
    if p1!=p2:
        print('Passwords do not match'); sys.exit(1)
    salt=os.urandom(16).hex()
    h=hashlib.sha256((salt+p1).encode()).hexdigest()
    data={'salt':salt,'hash':h}
    with open(CONF,'w') as f: json.dump(data,f)
    print('Password set and saved to',CONF)
def verify_password(pw):
    if not os.path.exists(CONF):
        print('No instructor password set. Use this script with no args to set one.'); return False
    d=json.load(open(CONF))
    s=d['salt']; h=d['hash']
    return hashlib.sha256((s+pw).encode()).hexdigest()==h
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='check':
        pw=getpass.getpass('Instructor password: '); print('OK' if verify_password(pw) else 'INVALID')
    else:
        set_password()
