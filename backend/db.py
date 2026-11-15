from pathlib import Path
import json, sqlite3, os
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('PINTARAI_DB',str(ROOT/'data'/'pintarai_v2.db')))
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 conn=sqlite3.connect(DB)
 conn.row_factory=sqlite3.Row
 return conn

@contextmanager
def session():
 db=connect()
 try:
  with db: yield db
 finally:
  db.close()

def initialize():
 with session() as db:
  db.execute('CREATE TABLE IF NOT EXISTS lessons (id TEXT PRIMARY KEY, mode TEXT NOT NULL, grade INTEGER, subject TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)')
  db.execute('CREATE INDEX IF NOT EXISTS idx_lessons ON lessons(mode,grade,subject,status)')
  db.execute('CREATE TABLE IF NOT EXISTS source_audits (claim_id TEXT PRIMARY KEY, lesson_id TEXT NOT NULL, publication TEXT NOT NULL, payload TEXT NOT NULL)')
  if db.execute('SELECT COUNT(*) FROM lessons').fetchone()[0] == 0:
   data=json.loads((ROOT/'data'/'lessons_draft.json').read_text(encoding='utf8'))
   for item in data:
    db.execute('INSERT INTO lessons VALUES(?,?,?,?,?,?,?)',(item['id'],item['mode'],item.get('grade'),item['subject'],item['subtopic'],'draft',json.dumps(item,ensure_ascii=False)))
  if db.execute('SELECT COUNT(*) FROM source_audits').fetchone()[0] == 0:
   data=json.loads((ROOT/'data'/'audit_evidence_v1.8.json').read_text(encoding='utf8'))
   for item in data['records']:
    db.execute('INSERT INTO source_audits VALUES(?,?,?,?)',(item['claim_id'],item['lesson_id'],'HELD',json.dumps(item,ensure_ascii=False)))

def stats():
 with session() as db:
  lessons=db.execute('SELECT status,COUNT(*) n FROM lessons GROUP BY status').fetchall()
  qs=db.execute('SELECT COUNT(*) FROM source_audits').fetchone()[0]
  ready=db.execute("SELECT COUNT(*) FROM lessons WHERE status='approved'").fetchone()[0]
 return {'lessons':sum(x['n'] for x in lessons),'questions':qs,'approved_lessons':ready,'draft_lessons':sum(x['n'] for x in lessons if x['status']!='approved')}
