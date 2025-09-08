RECON PLAYBOOK (High-level manual procedure)
Purpose: Identify Bluetooth devices in range and gather benign metadata for inventory and risk assessment.
Steps (manual):
1. Ensure lab authorization and RF isolation.
2. Use local Bluetooth tools (BlueZ) to scan and log devices: list device names, MACs, RSSI, and class.
3. Record time, operator, and location for each scan. Save outputs to a session folder.
4. Perform passive logging (in controlled range) with approved sniffers; ensure you have permission to capture.
5. Produce a CSV inventory with columns: timestamp, mac, name, rssi, vendor, discoverable (yes/no), services (if known).
Detection & Mitigation notes:
- Monitor for unknown advertising devices; configure alerts for new MAC prefixes.
- Encourage devices to disable discoverable mode and enforce pair-only policies.
