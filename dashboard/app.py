from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
import os, glob, json, hmac, hashlib, time, secrets, collections
from functools import wraps
BASE=os.path.dirname(os.path.dirname(__file__))
CONFIG=os.path.join(BASE,'config','auth.json')
REPORTS=os.path.join(BASE,'reports')
USERS=os.path.join(BASE,'config','users.json')
ORGS=os.path.join(BASE,'config','orgs.json')
AUDIT=os.path.join(BASE,'sessions','audit_signed.log')

app=Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'change-this-secret'

# load config
if os.path.exists(CONFIG):
    cfg=json.load(open(CONFIG))
else:
    cfg={}
HMAC_KEY=cfg.get('hmac_key','replace-me')

def read_orgs():
    return json.load(open(ORGS)) if os.path.exists(ORGS) else []

# helper: append-audit signed with HMAC, append-only
def audit(msg):
    ts=int(time.time())
    entry={'ts':ts,'user':session.get('user','anon'),'msg':msg}
    payload=json.dumps(entry,separators=(',',':')).encode()
    sig=hmac.new(HMAC_KEY.encode(), payload, hashlib.sha256).hexdigest()
    with open(AUDIT,'a') as f:
        f.write(sig+' '+payload.decode()+'\n')

# auth decorators
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'): return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def ldap_authenticate(username,password):
    if not cfg.get('use_ldap',False):
        return False
    try:
        import ldap
    except Exception:
        return False
    try:
        l=ldap.initialize(cfg['ldap_url'])
        l.simple_bind_s(username,password)
        return True
    except Exception:
        return False

def local_auth(username,password):
    if not os.path.exists(USERS): return False
    users=json.load(open(USERS))
    u=users.get(username)
    if not u: return False
    salt=u['salt']; h=u['hash']
    return hashlib.sha256((salt+password).encode()).hexdigest()==h

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=request.form['username']; pw=request.form['password']
        if cfg.get('use_ldap',False) and ldap_authenticate(user,pw):
            session['user']=user; audit('login ldap'); return redirect(url_for('index'))
        if local_auth(user,pw):
            session['user']=user; audit('login local'); return redirect(url_for('index'))
        return 'Invalid credentials',401
    return render_template('login.html')

@app.route('/logout')
def logout():
    audit('logout'); session.clear(); return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    orgs = read_orgs()
    audit('view_index')
    return render_template('index_org.html', orgs=orgs)

@app.route('/org/<org_code>')
@login_required
def org_dashboard(org_code):
    orgs = read_orgs()
    org = next((o for o in orgs if o.get('code')==org_code), None)
    if not org: return 'Org not found',404
    metrics = compute_org_metrics(org_code)
    audit(f'view_org_dashboard {org_code}')
    return render_template('org_dashboard.html', org=org, metrics=metrics)

def compute_org_metrics(org_code):
    metrics = {'usage_count':0,'submissions':0,'practice_submissions':0,'last_activity':None}
    # count filenames in reports/students that contain the org_code
    student_reports = glob.glob(os.path.join(REPORTS,'students','*'))
    for f in student_reports:
        if org_code in os.path.basename(f):
            metrics['submissions'] += 1
    practice = glob.glob(os.path.join(REPORTS,'practice_submissions','*'))
    for p in practice:
        if org_code in os.path.basename(p):
            metrics['practice_submissions'] += 1
    # parse audit log for lines containing org_code
    if os.path.exists(AUDIT):
        with open(AUDIT) as fh:
            for line in fh:
                try:
                    sig, payload = line.strip().split(' ',1)
                    if org_code in payload:
                        metrics['usage_count'] += 1
                        metrics['last_activity'] = json.loads(payload).get('ts')
                except Exception:
                    continue
    return metrics

# instructor routes same as before...
def instructor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        u=session.get('user')
        if not u: return redirect(url_for('login'))
        users=json.load(open(USERS)) if os.path.exists(USERS) else {}
        role=users.get(u,{}).get('role','student')
        if role not in ('instructor','redteam'): return 'Forbidden',403
        return f(*args, **kwargs)
    return decorated

@app.route('/instructor')
@login_required
@instructor_required
def instructor_dashboard():
    files=sorted(glob.glob(os.path.join(REPORTS,'students','*_*')), reverse=True)
    audit('instructor_view_reports')
    return render_template('instructor.html', files=[os.path.basename(f) for f in files])

@app.route('/instructor/release', methods=['POST'])
@login_required
@instructor_required
def release_grade():
    data=request.form
    student=data.get('student'); module=data.get('module'); grade=data.get('grade')
    outdir=os.path.join(REPORTS,'students')
    os.makedirs(outdir, exist_ok=True)
    rec={'student':student,'module':module,'grade':grade,'released_by':session.get('user'),'ts':int(time.time())}
    open(os.path.join(outdir,f'{student}_{module}_release.json'),'w').write(json.dumps(rec,indent=2))
    audit(f'release_grade {student} {module} {grade}')
    return redirect(url_for('instructor_dashboard'))

@app.route('/practice', methods=['GET','POST'])
@login_required
def practice():
    if request.method=='POST':
        if 'report' not in request.files: return 'No file',400
        f=request.files['report']; data=f.read().decode()
        try:
            j=json.loads(data)
        except Exception as e:
            return 'Invalid JSON',400
        hints=[]
        if 'module' not in j: hints.append('Report missing module field.')
        if 'timestamp' not in j: hints.append('Report missing timestamp.')
        if 'summary' not in j and 'attempts' not in j and 'profiles' not in j: hints.append('Report lacks summary/attempts/profiles.')
        resp={'ok': len(hints)==0, 'hints': hints}
        outdir=os.path.join(REPORTS,'practice_submissions'); os.makedirs(outdir, exist_ok=True)
        fname=os.path.join(outdir,f'{session.get("user")}_{int(time.time())}.json'); open(fname,'w').write(json.dumps(j,indent=2))
        audit(f'practice_submit user={session.get("user")} file={fname} ok={resp["ok"]}')
        return jsonify(resp)
    return render_template('practice.html')

@app.route('/orgs', methods=['GET','POST'])
@login_required
@instructor_required
def orgs_manage():
    if request.method=='POST':
        name=request.form['name']; code=request.form['code']
        orgs = json.load(open(ORGS)) if os.path.exists(ORGS) else []
        orgs.append({'name':name,'code':code,'created_by':session.get('user'),'ts':int(time.time())})
        open(ORGS,'w').write(json.dumps(orgs,indent=2))
        audit(f'org_create {name} by {session.get("user")}')
        return redirect(url_for('orgs_manage'))
    orgs = json.load(open(ORGS)) if os.path.exists(ORGS) else []
    return render_template('orgs.html', orgs=orgs)

@app.route('/download_audit')
@login_required
@instructor_required
def download_audit():
    if not os.path.exists(AUDIT): return 'No audit',404
    return send_file(AUDIT, as_attachment=True)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/org/<org_code>/trends')
@login_required
def org_trends(org_code):
    # Return timeseries of usage events per day for the last 30 days
    days=30
    now=int(time.time())
    counts=[0]*days
    labels=[]
    for i in range(days):
        ts_day = now - (days-i-1)*86400
        labels.append(time.strftime('%Y-%m-%d', time.localtime(ts_day)))
    if os.path.exists(AUDIT):
        with open(AUDIT) as fh:
            for line in fh:
                try:
                    sig, payload = line.strip().split(' ',1)
                    j=json.loads(payload)
                    ts=j.get('ts',0)
                    # check org_code in payload
                    if org_code in payload:
                        # map to day index
                        idx = int((ts - (now - (days-1)*86400))//86400)
                        if 0 <= idx < days:
                            counts[idx]+=1
                except Exception:
                    continue
    return jsonify({'labels':labels,'counts':counts})

@app.route('/org/<org_code>/export')
@login_required
def org_export(org_code):
    # CSV or XLSX export of org submissions and practice uploads
    fmt = request.args.get('fmt','csv')
    rows=[]
    # collect student submissions
    for p in glob.glob(os.path.join(REPORTS,'students','*')):
        if org_code in os.path.basename(p):
            rows.append({'type':'student_report','file':os.path.basename(p)})
    for p in glob.glob(os.path.join(REPORTS,'practice_submissions','*')):
        if org_code in os.path.basename(p):
            rows.append({'type':'practice_submission','file':os.path.basename(p)})
    # CSV
    import io
    si = io.StringIO()
    import csv
    w = csv.DictWriter(si, fieldnames=['type','file'])
    w.writeheader(); w.writerows(rows)
    csv_data = si.getvalue()
    if fmt == 'csv' or fmt == 'CSV':
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':f'attachment;filename={org_code}_export.csv'})
    # try xlsx using pandas if available
    try:
        import pandas as pd
        df = pd.DataFrame(rows)
        out = io.BytesIO(); df.to_excel(out, index=False, sheet_name=org_code)
        out.seek(0)
        return send_file(out, download_name=f'{org_code}_export.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception:
        # fallback to csv
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':f'attachment;filename={org_code}_export.csv'})


@app.route('/org/<org_code>/hourly')
@login_required
def org_hourly_pattern(org_code):
    # returns counts per hour for last 48 hours
    now = int(time.time())
    hours = 48
    counts = [0]*hours
    labels = []
    for i in range(hours):
        ts = now - (hours - i - 1)*3600
        labels.append(time.strftime('%Y-%m-%d %H:00', time.localtime(ts)))
    if os.path.exists(AUDIT):
        with open(AUDIT) as fh:
            for line in fh:
                try:
                    sig, payload = line.strip().split(' ',1)
                    if org_code in payload:
                        j = json.loads(payload)
                        ts = j.get('ts',0)
                        idx = int((ts - (now - (hours-1)*3600))//3600)
                        if 0 <= idx < hours:
                            counts[idx]+=1
                except Exception:
                    continue
    return jsonify({'labels':labels,'counts':counts})

@app.route('/org/<org_code>/heatmap')
@login_required
def org_heatmap(org_code):
    # returns matrix days x hours for last 14 days
    days = 14
    hours = 24
    matrix = [[0]*hours for _ in range(days)]
    start = int(time.time()) - (days*86400)
    if os.path.exists(AUDIT):
        with open(AUDIT) as fh:
            for line in fh:
                try:
                    sig, payload = line.strip().split(' ',1)
                    if org_code in payload:
                        j = json.loads(payload); ts = j.get('ts',0)
                        if ts >= start:
                            day_idx = int((ts - start)//86400)
                            hour_idx = int((ts % 86400)//3600)
                            if 0 <= day_idx < days and 0 <= hour_idx < hours:
                                matrix[day_idx][hour_idx] += 1
                except Exception:
                    continue
    labels_days = [time.strftime('%Y-%m-%d', time.localtime(start + i*86400)) for i in range(days)]
    return jsonify({'days':labels_days,'hours':list(range(0,24)),'matrix':matrix})

@app.route('/org/<org_code>/schedule_report', methods=['POST'])
@login_required
def schedule_report(org_code):
    # simple trigger to generate and email report for org (uses tools/schedule_report.py)
    import subprocess, shlex
    cmd = f"python3 {os.path.join(BASE,'tools','schedule_report.py')} {org_code}"
    p = subprocess.Popen(shlex.split(cmd))
    audit(f'schedule_report_trigger org={org_code} user={session.get("user")}' )
    return jsonify({'started':True})
