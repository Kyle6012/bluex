# Blue-X Deployment & Usage Guide

This guide walks through deploying the Blue-X dashboard and services in an internal environment.

## Prerequisites
- A secure internal host (Ubuntu 20.04+/RHEL 8+) with Python3 and pip.
- TLS certificate for dashboard (NGINX reverse proxy recommended).
- Optional: LDAP/AD access for authentication.

## Steps
1. Unzip the package to `/opt/bluex`.
2. Create a Python virtualenv and install requirements:
   ```bash
   python3 -m venv /opt/bluex/venv
   source /opt/bluex/venv/bin/activate
   pip install flask requests
   # optional:
   pip install python-ldap pdfkit reportlab
   ```
3. Configure `config/auth.json` (set hmac_key, LDAP options, SIEM endpoint/token).
4. Create users with `python3 tools/user_manage.py add --user alice --role instructor` or use LDAP/SSO.
5. Set up systemd timer: copy `systemd/bluex_export.service` and `systemd/bluex_export.timer` to `/etc/systemd/system/`, update ExecStart paths, then:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now bluex_export.timer
   ```
6. Run the dashboard behind NGINX+gunicorn for production.

## SIEM Export
- `tools/export_audit_signed_encrypt.py` bundles and encrypts the audit file; SIEM token in config is used as passphrase if provided.
- Alternatively run `tools/export_audit.py` to HTTP POST raw audit data.

## Security Notes
- Rotate `hmac_key` and any tokens periodically; restrict access to config files.
- Run the dashboard via a dedicated service account and restrict network access.

