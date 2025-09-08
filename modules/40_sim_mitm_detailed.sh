#!/usr/bin/env bash
# MODULE_NAME: SIM_MITM_DETAILED
# MODULE_DESC: Simulate a BLE MITM flow with detailed step-by-step logs and fake PCAP metadata (NO RADIO)
# MODULE_REQUIRES: python3, jq
set -euo pipefail
report_path="${1:-../reports/sim_mitm_detailed_$(date +%s).json}"
log_path="../sessions/sim_mitm_detailed_$(date +%s).log"
sim_pcap="../logs/sim_mitm_$(date +%s).pcapmeta.json"
echo "SIMULATION: Detailed BLE MITM flow (no radio)."
echo "Log: $log_path"
echo "Report: $report_path"
echo "SIM PCAP metadata: $sim_pcap"
echo "Starting simulated discovery..." | tee "$log_path"

python3 - "$report_path" <<'PY' | tee -a "$log_path"
import time, json, random, sys
report_path = sys.argv[1] if len(sys.argv)>1 else 'sim_mitm_report.json'
steps=[]
t0=int(time.time())
steps.append({'step':'scan_start','time':int(time.time()),'msg':'Scanning (simulated) for advertisements...'})
time.sleep(0.1)
devices=[{'addr':'AA:BB:CC:11:22:33','name':'SimSensor_1','rssi':-45},{'addr':'AA:BB:CC:44:55:66','name':'SimLock','rssi':-70}]
steps.append({'step':'scan_result','time':int(time.time()),'devices':devices})
time.sleep(0.1)
steps.append({'step':'gatt_enumeration','time':int(time.time()),'services':[{'uuid':'00001800-0000-1000-8000-00805f9b34fb','name':'Generic Access'},{'uuid':'00001801-0000-1000-8000-00805f9b34fb','name':'Generic Attribute'}]})
time.sleep(0.1)
pairing={'method':'JustWorks','timestamp':int(time.time()),'status':'simulated_capture','notes':'Pairing exchange captured to fake pcap metadata'}
steps.append({'step':'pairing_capture','time':int(time.time()),'pairing':pairing})
time.sleep(0.1)
steps.append({'step':'mitm_establish','time':int(time.time()),'status':'simulated','info':'Proxy created between attacker-peripheral and central - traffic not forwarded in safe mode'})
time.sleep(0.1)
collected=[{'type':'adv','count':120},{'type':'gatt_read','count':15},{'type':'gatt_write','count':3}]
steps.append({'step':'collect','time':int(time.time()),'collected':collected})
summary={'risk':'medium','confidence':0.65,'notes':'Simulation only. In real tests, verify ATT handles and encryption.'}
report={'module':'SIM_MITM_DETAILED','timestamp':t0,'steps':steps,'summary':summary}
open(report_path,'w').write(json.dumps(report,indent=2))
print('WROTE', report_path)
PY

# create fake pcap metadata JSON (describes packets but is NOT a pcap)
python3 - <<'PY' > "$sim_pcap"
import json, time, random
meta={'file':'sim_mitm.pcap','captured_at':int(time.time()),'packets':[]}
for i in range(30):
    meta['packets'].append({'seq':i,'ts':int(time.time())-30+i,'proto':'BTLE','len':random.randint(30,120),'type':random.choice(['ADV','ATT','GATT_READ','GATT_WRITE'])})
print(json.dumps(meta,indent=2))
PY

echo "SIMULATION COMPLETE. See logs and report."
