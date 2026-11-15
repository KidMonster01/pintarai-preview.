from pathlib import Path
from contextlib import asynccontextmanager
import json, os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
import base64, hmac
from fastapi.staticfiles import StaticFiles
from .db import initialize, session, stats
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web'
DEMO=os.getenv('PINTARAI_DEMO_PREVIEW','0')=='1'
SITE_MODE=os.getenv('PINTARAI_SITE_MODE','production').strip().lower()
if SITE_MODE not in ('production','preview'): SITE_MODE='production'
PREVIEW_PASSWORD=os.getenv('PINTARAI_PREVIEW_PASSWORD','')
@asynccontextmanager
async def lifespan(app):
 initialize()
 yield
app=FastAPI(title='PintarAI API',version='2.1-preview',docs_url='/api/docs',redoc_url=None,lifespan=lifespan)

@app.middleware('http')
async def preview_and_security_gate(request:Request,call_next):
 path=request.url.path
 in_student_app=path=='/app' or path.startswith('/app/')
 if in_student_app and SITE_MODE!='preview':
  return HTMLResponse('<!doctype html><html lang="id"><meta charset="utf-8"><title>PintarAI</title><main style="font:16px system-ui;max-width:560px;margin:15vh auto;padding:24px"><h1>🔒 PintarAI sedang dipersiapkan</h1><p>Konten akademik belum melewati Quality Gate. Aplikasi belum dibuka untuk publik.</p><a href="/">← Beranda</a></main></html>',status_code=503,headers={'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow'})
 if in_student_app and SITE_MODE=='preview' and PREVIEW_PASSWORD:
  header=request.headers.get('authorization','')
  authorized=False
  if header.startswith('Basic '):
   try:
    decoded=base64.b64decode(header.split(' ',1)[1],validate=True).decode('utf-8')
    _username, supplied=decoded.split(':',1)
    authorized=hmac.compare_digest(supplied,PREVIEW_PASSWORD)
   except (ValueError,UnicodeDecodeError): pass
  if not authorized:
   return PlainTextResponse('Preview PintarAI memerlukan kata sandi.',status_code=401,headers={'WWW-Authenticate':'Basic realm="PintarAI Preview"','Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow'})
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff'
 response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
 response.headers['X-Frame-Options']='DENY'
 response.headers['Permissions-Policy']='geolocation=(), camera=(), microphone=()'
 if path.startswith('/api/'):
  response.headers['Cache-Control']='no-store'
 if in_student_app or SITE_MODE=='preview':
  response.headers['X-Robots-Tag']='noindex, nofollow'
 return response

@app.get('/api/v1/health')
def health():return {'status':'ok','version':'2.1-preview','mode':SITE_MODE,'demo_preview':DEMO}

@app.get('/api/v1/status')
def public_status():
 s=stats()
 return {'mode':SITE_MODE,'student_app_enabled':SITE_MODE=='preview',
         'ai_tutor':'simulasi','approved_lessons':s['approved_lessons'],
         'content_notice':'Semua materi demo adalah draft belum diverifikasi akademik.'}

@app.get('/robots.txt',response_class=PlainTextResponse)
def robots():
 return 'User-agent: *\nDisallow: /app/\nDisallow: /api/\n'

@app.get('/api/v1/quality')
def quality():
 s=stats()
 s.update({'publication_gate':'fail_closed','ai_reviews_completed':0,'live_source_checks_completed':0,'note':'Tidak ada konten otomatis diterbitkan. Semua konten awal masih draft.'})
 return s

@app.get('/api/v1/lessons')
def lesson_list(grade:int|None=Query(default=None,ge=1,le=12),mode:str|None=None,subject:str|None=None,preview:bool=False,limit:int=Query(300,ge=1,le=500)):
 allow_preview=bool(preview and DEMO and SITE_MODE=='preview')
 sql='SELECT payload FROM lessons WHERE 1=1';args=[]
 if not allow_preview:sql+=" AND status='approved'"
 if grade is not None:sql+=' AND grade=?';args.append(grade)
 if mode in ('school','explore'):sql+=' AND mode=?';args.append(mode)
 if subject:sql+=' AND subject=?';args.append(subject)
 sql+=' ORDER BY CASE WHEN grade IS NULL THEN 100 ELSE grade END,subject,title LIMIT ?';args.append(limit)
 with session() as db:items=[json.loads(row['payload']) for row in db.execute(sql,args)]
 return {'preview':allow_preview,'items':items,'count':len(items),'verified':not allow_preview}

@app.get('/api/v1/lessons/{lesson_id}')
def lesson_detail(lesson_id:str,preview:bool=False):
 if len(lesson_id)>120:raise HTTPException(400,'Invalid id')
 with session() as db:row=db.execute('SELECT status,payload FROM lessons WHERE id=?',(lesson_id,)).fetchone()
 if not row:raise HTTPException(404,'Materi tidak ditemukan')
 if row['status']!='approved' and not (preview and DEMO and SITE_MODE=='preview'):raise HTTPException(404,'Materi belum lolos Quality Gate')
 return {'preview':row['status']!='approved','item':json.loads(row['payload'])}

# Static pages must come after API routes.
app.mount('/app',StaticFiles(directory=WEB/'app',html=True),name='student-app')
app.mount('/',StaticFiles(directory=WEB,html=True),name='website')
