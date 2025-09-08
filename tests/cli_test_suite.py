#!/usr/bin/env python3
"""Enhanced CLI test suite: runs simulation modules for a student, validates reports, and produces grading CSV and simple PDF (markdown->pdf) feedback."""
import subprocess, json, os, csv, sys, time
BASE=os.path.dirname(os.path.dirname(__file__))
REPORTS=os.path.join(BASE,'reports')
STUDENT_REPORTS=os.path.join(REPORTS,'students')
os.makedirs(STUDENT_REPORTS, exist_ok=True)
MODULES=[('SIM_MITM_DETAILED','modules/40_sim_mitm_detailed.sh'), ('SIM_PAIRING_DETAILED','modules/41_sim_pairing_detailed.sh'), ('SIM_FUZZ_DETAILED','modules/42_sim_fuzz_detailed.sh')]

def run_module(modpath, outjson):
    subprocess.run(['bash', modpath, outjson], check=True, capture_output=True, text=True)

def grade_report(repjson):
    rep=json.load(open(repjson))
    score=0; notes=[]
    if rep.get('module'): score+=10
    if rep.get('timestamp'): score+=5
    if rep.get('summary') or rep.get('attempts') or rep.get('profiles'): score+=10
    return score, notes

def make_markdown(student, results, total_score):
    md=f"""# Student Report - {student}\n\nTotal Score: {total_score}\n\n"""
    for r in results:
        md += f"## {r['module']}\nScore: {r['score']}\nNotes: {r['notes']}\nReport: {r['report']}\n\n"
    return md

if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage: cli_test_suite.py student_name'); sys.exit(1)
    student=sys.argv[1]
    results=[]; total=0
    for modname, modpath in MODULES:
        outjson=os.path.join(REPORTS, f"{student}_{modname}.json")
        try:
            run_module(modpath, outjson)
            score, notes = grade_report(outjson)
            results.append({'module':modname,'score':score,'notes':' '.join(notes),'report':outjson})
            total+=score
        except Exception as e:
            results.append({'module':modname,'score':0,'notes':str(e),'report':''})
    # write CSV
    csvfile=os.path.join(STUDENT_REPORTS, f"{student}_grading.csv")
    with open(csvfile,'w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['module','score','notes','report'])
        w.writeheader(); w.writerows(results)
    # write markdown and convert to pdf (if possible)
    md=make_markdown(student, results, total)
    mdpath=os.path.join(STUDENT_REPORTS, f"{student}_report.md")
    open(mdpath,'w').write(md)
    pdfpath=os.path.join(STUDENT_REPORTS, f"{student}_report.pdf")
    # try to convert
    ret = subprocess.call(['python3', os.path.join(BASE,'tools','md_to_pdf.py'), mdpath, pdfpath])
    print('WROTE', csvfile, mdpath, 'PDF conversion rc', ret)
