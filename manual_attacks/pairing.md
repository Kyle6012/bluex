PAIRING ANALYSIS PLAYBOOK (High-level manual guidance)
Purpose: Analyze pairing methods and test enforcement of secure pairing modes.
Manual steps:
1. Enumerate pairing options supported by the device (JustWorks, Passkey, Numeric Compare).
2. Attempt authorized pairing flows in a controlled test device; document prompts and required user interaction.
3. Do not attempt pairing bypasses without explicit written consent.
Detection & Mitigation:
- Enforce secure pairing (Numeric Compare or PasskeyEntry) where possible; disable JustWorks for sensitive devices.
