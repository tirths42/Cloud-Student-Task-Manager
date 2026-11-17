"""Cloud-Based Student Task Manager for GMIU cloud computing activity."""
import os, uuid, logging, sqlite3
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'))
log=logging.getLogger('cloud_task_manager')
app=Flask(__name__)
PROJECT_ID=os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCP_PROJECT_ID')
DATABASE_ID=os.getenv('FIRESTORE_DATABASE','(default)')
COLLECTION=os.getenv('FIRESTORE_COLLECTION','tasks')
_firestore=None
_firestore_error=None

def now(): return datetime.now(timezone.utc).isoformat()
def firestore_client():
    global _firestore,_firestore_error
    if _firestore is not None: return _firestore
    if not PROJECT_ID:
        _firestore_error='Set GOOGLE_CLOUD_PROJECT to enable Firestore.'
        return None
    try:
        from google.cloud import firestore
        _firestore=firestore.Client(project=PROJECT_ID,database=DATABASE_ID)
        _firestore_error=None
        return _firestore
    except Exception as exc:
        _firestore_error=str(exc); log.warning('Firestore unavailable: %s',exc); return None

def local_db():
    conn=sqlite3.connect(os.getenv('LOCAL_DB_PATH','tasks.db')); conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL, due_date TEXT NOT NULL, is_completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)')
    conn.commit(); return conn

class Store:
    def __init__(self): self.fs=firestore_client()
    @property
    def mode(self): return 'cloud_firestore' if self.fs else 'local_sqlite'
    def list(self):
        if self.fs:
            out=[]
            for d in self.fs.collection(COLLECTION).stream(): out.append((d.to_dict() or {}) | {'task_id':d.id})
            return sorted(out,key=lambda x:x.get('created_at',''),reverse=True)
        with local_db() as c: return [dict(r)|{'is_completed':bool(r['is_completed'])} for r in c.execute('SELECT * FROM tasks ORDER BY created_at DESC')]
    def get(self,tid):
        if self.fs:
            d=self.fs.collection(COLLECTION).document(tid).get()
            return ((d.to_dict() or {})|{'task_id':d.id}) if d.exists else None
        with local_db() as c:
            r=c.execute('SELECT * FROM tasks WHERE task_id=?',(tid,)).fetchone()
            return (dict(r)|{'is_completed':bool(r['is_completed'])}) if r else None
    def create(self,x):
        if self.fs: self.fs.collection(COLLECTION).document(x['task_id']).set(x)
        else:
            with local_db() as c: c.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)',(x['task_id'],x['title'],x['subject'],x['description'],x['priority'],x['due_date'],0,x['created_at'],x['updated_at']))
    def update(self,tid,changes):
        if self.fs:
            ref=self.fs.collection(COLLECTION).document(tid)
            if not ref.get().exists:return False
            ref.update(changes);return True
        allowed=('title','subject','description','priority','due_date','is_completed','updated_at')
        pairs=[(k,v) for k,v in changes.items() if k in allowed]
        if not pairs:return False
        sets=','.join(k+'=?' for k,v in pairs); vals=[int(v) if k=='is_completed' else v for k,v in pairs]
        with local_db() as c: return c.execute('UPDATE tasks SET '+sets+' WHERE task_id=?',vals+[tid]).rowcount>0
    def delete(self,tid):
        if self.fs:
            ref=self.fs.collection(COLLECTION).document(tid)
            if not ref.get().exists:return False
            ref.delete();return True
        with local_db() as c:return c.execute('DELETE FROM tasks WHERE task_id=?',(tid,)).rowcount>0

def validate(data):
    title=str(data.get('title','')).strip(); subject=str(data.get('subject','General')).strip() or 'General'; desc=str(data.get('description','')).strip(); priority=str(data.get('priority','Medium')).capitalize(); due=str(data.get('due_date','')).strip()
    if not title:return None,'Task title is required.'
    if len(title)>120:return None,'Title must be 120 characters or fewer.'
    if len(subject)>60:return None,'Subject must be 60 characters or fewer.'
    if len(desc)>1000:return None,'Description must be 1000 characters or fewer.'
    if priority not in ('Low','Medium','High'):return None,'Priority must be Low, Medium or High.'
    return {'title':title,'subject':subject,'description':desc,'priority':priority,'due_date':due},None

@app.get('/')
def index(): return render_template('index.html')
@app.get('/health')
def health(): return jsonify({'status':'ok','time':now()})
@app.get('/api/status')
def status():
    s=Store(); run=bool(os.getenv('K_SERVICE'))
    return jsonify({'status':'healthy','compute':{'platform':'Google Cloud Run' if run else 'Local development','is_cloud_run':run,'service':os.getenv('K_SERVICE'),'region':os.getenv('CLOUD_RUN_REGION')},'storage':{'service':'Google Cloud Firestore' if s.fs else 'Local SQLite (development fallback)','connected':bool(s.fs),'mode':s.mode,'collection':COLLECTION if s.fs else None,'error':None if s.fs else _firestore_error}})
@app.get('/api/tasks')
def list_tasks():
    try:
        s=Store(); tasks=s.list(); sf=request.args.get('status','all').lower(); pf=request.args.get('priority','all').capitalize(); q=request.args.get('search','').strip().lower()
        if sf not in ('all','pending','completed') or pf not in ('All','Low','Medium','High'):return jsonify({'success':False,'error':'Invalid filter.'}),400
        out=[]
        for t in tasks:
            done=bool(t.get('is_completed',False))
            if sf=='pending' and done:continue
            if sf=='completed' and not done:continue
            if pf!='All' and t.get('priority')!=pf:continue
            if q and not any(q in str(t.get(k,'')).lower() for k in ('title','subject','description')):continue
            out.append(t)
        return jsonify({'success':True,'storage':s.mode,'total_count':len(tasks),'filtered_count':len(out),'tasks':out})
    except Exception:
        log.exception('List task failure');return jsonify({'success':False,'error':'Unable to read tasks. Check database setup and logs.'}),503
@app.post('/api/tasks')
def create_task():
    x,err=validate(request.get_json(silent=True) or {})
    if err:return jsonify({'success':False,'error':err}),400
    x|={'task_id':str(uuid.uuid4()),'is_completed':False,'created_at':now(),'updated_at':now()}
    try:
        s=Store();s.create(x);return jsonify({'success':True,'message':'Task created.','task':x,'storage':s.mode}),201
    except Exception:
        log.exception('Create task failure');return jsonify({'success':False,'error':'Unable to save task. Check Firestore permissions or local storage.'}),503
@app.put('/api/tasks/<tid>')
def update_task(tid):
    x,err=validate(request.get_json(silent=True) or {})
    if err:return jsonify({'success':False,'error':err}),400
    x['updated_at']=now()
    try:
        s=Store()
        if not s.update(tid,x):return jsonify({'success':False,'error':'Task not found.'}),404
        return jsonify({'success':True,'message':'Task updated.','storage':s.mode})
    except Exception:
        log.exception('Update task failure');return jsonify({'success':False,'error':'Unable to update task.'}),503
@app.patch('/api/tasks/<tid>/toggle')
def toggle_task(tid):
    try:
        s=Store();x=s.get(tid)
        if not x:return jsonify({'success':False,'error':'Task not found.'}),404
        done=not bool(x.get('is_completed',False));s.update(tid,{'is_completed':done,'updated_at':now()})
        return jsonify({'success':True,'is_completed':done,'storage':s.mode})
    except Exception:
        log.exception('Toggle failure');return jsonify({'success':False,'error':'Unable to update task status.'}),503
@app.delete('/api/tasks/<tid>')
def delete_task(tid):
    try:
        s=Store()
        if not s.delete(tid):return jsonify({'success':False,'error':'Task not found.'}),404
        return jsonify({'success':True,'message':'Task deleted.','storage':s.mode})
    except Exception:
        log.exception('Delete failure');return jsonify({'success':False,'error':'Unable to delete task.'}),503
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.getenv('PORT','8080')),debug=False)
