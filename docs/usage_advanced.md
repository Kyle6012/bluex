# Blue-X: Per-org Exports, SIEM Integration, and Ansible Deployment

## Per-org trends & exports
- Visit /org/<org_code> for metrics and click 'Load 30-day activity' to see trends.
- Click 'Download CSV' or 'Download XLSX' to export org submissions. XLSX requires pandas and openpyxl installed in the venv.

## SIEM Integrations
- Configure splunk or elastic settings under config/auth.json -> siem.
- Use tools/splunk_hec.py to push audit lines to Splunk HEC (configure endpoint/token).
- Use tools/elastic_ingest.py to push audit lines to Elasticsearch bulk API (configure endpoint/index).
- For automated secure export/encrypt and remote transfer, configure systemd timer and use tools/export_audit_signed_encrypt.py.

## Ansible Deployment
- Copy the package to your Ansible control host as 'bluex_safe_sim' directory.
- Edit ansible/playbook.yml to point to your inventory and run:
  ansible-playbook -i inventory.ini ansible/playbook.yml
- Customize the role tasks to match your environment and secure file paths.
