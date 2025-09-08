# Blue-X Safe Simulation Pack

**Author:** Meshack Bahati Ouma
 
**Purpose:** A _safe_ educational framework for learning Bluetooth pentest workflows.

This package intentionally avoids radio transmissions or exploit code. It provides:

- A smart installer that maps packages per distro and installs only benign dependencies.
- Simulation modules that emulate MITM, pairing, and fuzzing flows and generate JSON/CSV session reports.
- A simple Flask-based HTML dashboard to view session reports.
- `--safe` mode and clear warnings.

Use this in classrooms and labs to practice workflows, reporting, and analysis. Do NOT use on real targets without authorization.

## Instructor Lock Setup

To set the instructor password (required to enable Attack Mode helper):

```
python3 tools/instructor_manage.py
```

To check a password:

```
python3 tools/instructor_manage.py check
```

All Attack Mode uses are audited to `sessions/audit.log`.

## New Features: Per-org dashboards, SIEM export scheduling, LDAP/SSSD guide

See docs/deployment_guide.md and docs/ldap_sssd_ad.md
