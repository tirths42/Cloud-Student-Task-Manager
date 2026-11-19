"""Cloud-Based Student Task Manager for GMIU cloud computing activity."""
import os, uuid, logging, sqlite3
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'))
log=logging.getLogger('cloud_task_manager')
app=Flask(__name__)
SUPABASE_URL=os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
COLLECTION=os.getenv('SUPABASE_TABLE','tasks')
_supabase=None
_supabase_error=None

def now(): return datetime.now(timezone.utc).isoformat()
def supabase_client():
    """Return a server-side Supabase client, or None when not configured."""
    global _supabase, _supabase_error
    if _supabase is not None:
        return _supabase
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        _supabase_error='Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to enable cloud PostgreSQL.'
        return None
    try:
        from supabase import create_client
        _supabase=create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        _supabase_error=None
        return _supabase
    except Exception as exc:
        _supabase_error=str(exc)
        log.warning('Supabase unavailable: %s', exc)
        return None

def local_db():
    conn=sqlite3.connect(os.getenv('LOCAL_DB_PATH','tasks.db')); conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL, due_date TEXT NOT NULL, is_completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)')
    conn.commit(); return conn

class Store:
    def __init__(self):
        self.sb=supabase_client()

    @property
    def mode(self):
        return 'supabase_postgres' if self.sb else 'local_sqlite'

    def list(self):
        if self.sb:
            result=self.sb.table(COLLECTION).select('*').order('created_at', desc=True).execute()
            return result.data or []
        with local_db() as c:
            return [dict(r)|{'is_completed':bool(r['is_completed'])} for r in c.execute('SELECT * FROM tasks ORDER BY created_at DESC')]

    def get(self,tid):
        if self.sb:
            result=self.sb.table(COLLECTION).select('*').eq('task_id',tid).limit(1).execute()
            return result.data[0] if result.data else None
        with local_db() as c:
            r=c.execute('SELECT * FROM tasks WHERE task_id=?',(tid,)).fetchone()
            return (dict(r)|{'is_completed':bool(r['is_completed'])}) if r else None

    def create(self,x):
        if self.sb:
            self.sb.table(COLLECTION).insert(x).execute()
        else:
            with local_db() as c:
                c.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)',(x['task_id'],x['title'],x['subject'],x['description'],x['priority'],x['due_date'],0,x['created_at'],x['updated_at']))

    def update(self,tid,changes):
        if self.sb:
            result=self.sb.table(COLLECTION).update(changes).eq('task_id',tid).select('*').execute()
            return bool(result.data)
        allowed=('title','subject','description','priority','due_date','is_completed','updated_at')
        pairs=[(k,v) for k,v in changes.items() if k in allowed]
        if not pairs:return False
        sets=','.join(k+'=?' for k,v in pairs); vals=[int(v) if k=='is_completed' else v for k,v in pairs]
        with local_db() as c:
            return c.execute('UPDATE tasks SET '+sets+' WHERE task_id=?',vals+[tid]).rowcount>0

    def delete(self,tid):
        if self.sb:
            result=self.sb.table(COLLECTION).delete().eq('task_id',tid).select('*').execute()
            return bool(result.data)
        with local_db() as c:
            return c.execute('DELETE FROM tasks WHERE task_id=?',(tid,)).rowcount>0

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
    s=Store(); render=bool(os.getenv('RENDER'))
    return jsonify({'status':'healthy','compute':{'platform':'Render' if render else 'Local development','is_render':render,'service':os.getenv('RENDER_SERVICE_NAME')},'storage':{'service':'Supabase PostgreSQL' if s.sb else 'Local SQLite (development fallback)','connected':bool(s.sb),'mode':s.mode,'table':COLLECTION if s.sb else None,'error':None if s.sb else _supabase_error}})
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
        log.exception('Create task failure');return jsonify({'success':False,'error':'Unable to save task. Check Supabase table/credentials or local storage.'}),503
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
