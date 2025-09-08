GATT ENUMERATION PLAYBOOK (High-level manual procedure)
Purpose: Manually enumerate GATT services and characteristics on target devices for mapping attack surface.
Steps (manual):
1. Confirm authorization and scope (specific devices and time window).
2. Using approved tools (gatttool/gattacker/btgatt-client manually), perform controlled reads of public characteristics.
3. Document service UUIDs, characteristic properties (read/write/notify), and any open descriptors.
4. Save outputs and ensure you DO NOT write to characteristics unless explicitly authorized.
Detection & Mitigation:
- Block insecure GATT characteristics, enforce authentication on write operations, and monitor for unexpected read/write traffic.
