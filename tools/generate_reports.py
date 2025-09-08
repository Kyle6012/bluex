#!/usr/bin/env python3
import json, csv, glob, os
BASE=os.path.dirname(os.path.dirname(__file__))
REPORTS=os.path.join(BASE,'reports')
OUT_CSV=os.path.join(BASE,'reports','aggregated_reports.csv')
json_files=glob.glob(os.path.join(REPORTS,'*.json'))
rows=[]
for jf in json_files:
    try:
        j=json.load(open(jf))
        module=j.get('module', 'unknown')
        ts=j.get('timestamp','')
        summary=j.get('summary',{})
        rows.append({'file':os.path.basename(jf),'module':module,'timestamp':ts,'summary':json.dumps(summary)})
    except Exception as e:
        rows.append({'file':os.path.basename(jf),'module':'error','timestamp':'','summary':str(e)})
with open(OUT_CSV,'w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['file','module','timestamp','summary'])
    w.writeheader()
    w.writerows(rows)
print('WROTE', OUT_CSV)
