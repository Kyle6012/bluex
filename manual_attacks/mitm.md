MITM ORCHESTRATION PLAYBOOK (High-level manual guidance)
Purpose: For authorized red-team exercises only. This describes the operator workflow without automation.
Operator responsibilities (manual):
- Establish secure lab and capture full logs before any action.
- Use manual orchestration to create a fake peripheral or central (tools exist), but operators must run steps interactively.
- Record exact commands executed, timestamps, and stdout/stderr to session logs.
- Always have a rollback plan; do not leave devices in an unknown state.
Detection & Mitigation:
- Validate pairing integrity, enable secure pairing modes, and log pairing attempts for anomaly detection.
