#!/usr/bin/env python3
"""User management for Blue-X: add/list/delete users and set roles.
Users stored in config/users.json as {'username':{'salt':..., 'hash':..., 'role':...}}"""
import os, sys, json, getpass, hashlib, binascii
BASE=os.path.dirname(os.path.dirname(__file__))
USERS=os.path.join(BASE,'config','users.json')
os.makedirs(os.path.dirname(USERS), exist_ok=True)
def load_users():
    if not os.path.exists(USERS): return {}
    return json.load(open(USERS))
def save_users(u): json.dump(u, open(USERS,'w'), indent=2)
def make_hash(pw, salt=None):
    if salt is None: salt=binascii.hexlify(os.urandom(16)).decode()
    h=hashlib.sha256((salt+pw).encode()).hexdigest()
    return salt,h
def add_user(username, role):
    users=load_users()
    if username in users: print('User exists'); return
    pw=getpass.getpass('Password for %s: '%username)
    pw2=getpass.getpass('Confirm: ')
    if pw!=pw2: print('Mismatch'); return
    salt,h=make_hash(pw)
    users[username]={'salt':salt,'hash':h,'role':role}
    save_users(users); print('User added')
def check_user(username, pw):
    users=load_users()
    u=users.get(username)
    if not u: return False
    salt=u['salt']; h=u['hash']
    return hashlib.sha256((salt+pw).encode()).hexdigest()==h
def list_users():
    users=load_users()
    for k,v in users.items():
        print(k, v.get('role'))
def delete_user(username):
    users=load_users()
    if username in users: del users[username]; save_users(users); print('Deleted')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('action', choices=['add','list','del','check'])
    p.add_argument('--user', '-u')
    p.add_argument('--role', '-r', default='student')
    args=p.parse_args()
    if args.action=='add' and args.user:
        add_user(args.user, args.role)
    elif args.action=='list':
        list_users()
    elif args.action=='del' and args.user:
        delete_user(args.user)
    elif args.action=='check' and args.user:
        pw=getpass.getpass('Password: '); print('OK' if check_user(args.user,pw) else 'INVALID')
    else:
        print('Invalid usage')