#!/usr/bin/env python3
"""Export audit file: optionally sign (already HMAC-signed per-line) and encrypt with openssl AES-256-CBC using a passphrase from config.
Usage: tools/export_audit_signed_encrypt.py --out /tmp/export.tar.gz.enc
"""
import os, json, subprocess, sys
BASE=os.path.dirname(os.path.dirname(__file__))
CONF=os.path.join(BASE,'config','auth.json')
AUDIT=os.path.join(BASE,'sessions','audit_signed.log')
cfg=json.load(open(CONF)) if os.path.exists(CONF) else {}
passphrase=cfg.get('siem',{}).get('http_token','') or os.environ.get('BLUEX_SIEM_PASSPHRASE','')
out = sys.argv[1] if len(sys.argv)>1 else None
if not out:
    print('Usage: export_audit_signed_encrypt.py <outfile>'); sys.exit(1)
if not os.path.exists(AUDIT):
    print('No audit file'); sys.exit(1)
# tar the audit file
import tarfile, time
tmp = '/tmp/bluex_audit_{}.tar.gz'.format(int(time.time()))
with tarfile.open(tmp,'w:gz') as tar:
    tar.add(AUDIT, arcname='audit_signed.log')
# encrypt with openssl if passphrase available
if passphrase:
    cmd = ['openssl','enc','-aes-256-cbc','-salt','-in',tmp,'-out',out,'-pass','pass:' + passphrase]
    try:
        subprocess.check_call(cmd)
        print('WROTE', out)
    except Exception as e:
        print('OpenSSL failed:', e); sys.exit(2)
else:
    # fallback: just move tar to out
    os.rename(tmp, out)
    print('WROTE (unencrypted)', out)
