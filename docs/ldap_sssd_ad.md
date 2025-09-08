# LDAP / SSSD / Active Directory Integration Guide

This guide explains how to integrate Blue-X dashboard authentication with an enterprise LDAP/AD via SSSD and optionally python-ldap for direct binds.

## Overview
- Two options: (A) Configure SSSD on the host so system accounts are LDAP/AD users; (B) Enable LDAP direct bind in the Flask app by setting "use_ldap": true in `config/auth.json` and installing `python-ldap`.

## Example SSSD configuration (for Ubuntu/RHEL)
/etc/sssd/sssd.conf:
```
[sssd]
services = nss, pam
config_file_version = 2
domains = YOUR.DOMAIN

[domain/YOUR.DOMAIN]
id_provider = ad
access_provider = simple
simple_allow_groups = bluex_users
ad_domain = your.domain
krb5_realm = YOUR.DOMAIN
ldap_sudo_search_base = ou=SUDOers,dc=your,dc=domain
cache_credentials = True
enumerate = False
fallback_homedir = /home/%u
```
Set permissions: `chmod 600 /etc/sssd/sssd.conf` and restart sssd: `systemctl restart sssd`.

## Enable python-ldap in Flask (direct bind)
1. Install: `sudo pip3 install python-ldap`
2. In `config/auth.json` set:
```
"use_ldap": true,
"ldap_url": "ldap://ldap.your.domain",
"ldap_bind_dn": "cn=readonly,dc=your,dc=domain",
"ldap_base_dn": "dc=your,dc=domain"
```
3. The dashboard will attempt LDAP simple bind when users log in.

## Notes for Infra
- Ensure TLS (ldaps://) or STARTTLS is used in production to protect credentials.
- Work with AD team to create a service account for read binds or use Kerberos.
- Consider integrating with your SSO/AD FS for single sign-on instead.
