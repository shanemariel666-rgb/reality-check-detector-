import os, io, json, tempfile, sqlite3, secrets, datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
from passlib.hash import bcrypt
from PIL import Image, ImageChops, ImageStat
import numpy as np
import imagehash
import requests

DB_PATH = 'data.db'
app = FastAPI(title='Reality Check API')

DETECTOR_TYPE = os.environ.get('DETECTOR_TYPE','mock')
DETECTOR_API = os.environ.get('DETECTOR_API','')
HUGGINGFACE_KEY = os.environ.get('HUGGINGFACE_API_KEY','')
HF_MODEL = os.environ.get('HF_MODEL','')  # e.g. 'microsoft/xxx' appropriate detector

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, token TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (id TEXT PRIMARY KEY, user_id INTEGER, filename TEXT, verdict TEXT, score REAL, details TEXT, created_at TEXT, verified INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_user_by_token(token):
    if not token: return None
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT id,name,email FROM users WHERE token=?', (token,))
    row = c.fetchone(); conn.close()
    if not row: return None
    return {'id':row[0],'name':row[1],'email':row[2]}

def require_auth(authorization: str = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail='Missing Authorization header')
    parts = authorization.split()
    if len(parts)!=2 or parts[0].lower()!='bearer': raise HTTPException(status_code=401, detail='Invalid auth header')
    user = get_user_by_token(parts[1])
    if not user: raise HTTPException(status_code=401, detail='Invalid token')
    return user

@app.on_event('startup')
def startup():
    init_db()

@app.post('/api/register')
async def register(payload: dict):
    name = payload.get('name'); email = payload.get('email'); pwd = payload.get('pwd')
    if not name or not email or not pwd: return JSONResponse({'error':'Missing fields'}, status_code=400)
    hashed = bcrypt.hash(pwd)
    token = secrets.token_urlsafe(24)
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute('INSERT INTO users (name,email,password,token) VALUES (?,?,?,?)', (name,email,hashed,token))
        conn.commit()
    except Exception as e:
        conn.close(); return JSONResponse({'error':'Email already registered'}, status_code=400)
    conn.close()
    return JSONResponse({'token':token})

@app.post('/api/login')
async def login(payload: dict):
    email = payload.get('email'); pwd = payload.get('pwd')
    if not email or not pwd: return JSONResponse({'error':'Missing fields'}, status_code=400)
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT id,password FROM users WHERE email=?', (email,))
    row = c.fetchone()
    if not row: conn.close(); return JSONResponse({'error':'Invalid credentials'}, status_code=401)
    uid, hashed = row
    if not bcrypt.verify(pwd, hashed): conn.close(); return JSONResponse({'error':'Invalid credentials'}, status_code=401)
    token = secrets.token_urlsafe(24)
    c.execute('UPDATE users SET token=? WHERE id=?', (token, uid)); conn.commit(); conn.close()
    return JSONResponse({'token':token})

def get_exif(img):
    exif={}
    try:
        raw = img._getexif() or {}
        for k,v in raw.items():
            exif[str(k)] = str(v)
    except: pass
    return exif

def ela_score(img, quality=90):
    with io.BytesIO() as out:
        img.save(out, 'JPEG', quality=quality)
        out.seek(0)
        recompressed = Image.open(out).convert('RGB')
    ela = ImageChops.difference(img.convert('RGB'), recompressed)
    stat = ImageStat.Stat(ela)
    return sum(stat.mean)/len(stat.mean)

def blur_score(img):
    gray = img.convert('L')
    arr = np.array(gray, dtype=np.float32)
    gy,gx = np.gradient(arr)
    mag = np.sqrt(gx*gx + gy*gy)
    return float(mag.var())

def phash(img):
    h = imagehash.phash(img)
    return str(h), int(h.hash.sum())

def call_hf(image_bytes):
    if not HUGGINGFACE_KEY or not HF_MODEL: return {'error':'No HF configured'}
    headers = {'Authorization':f'Bearer {HUGGINGFACE_KEY}'}
    url = f'https://api-inference.huggingface.co/models/{HF_MODEL}'
    try:
        r = requests.post(url, headers=headers, data=image_bytes, timeout=30)
        return r.json()
    except Exception as e:
        return {'error':str(e)}

def call_external(url, files):
    try:
        r = requests.post(url, files=files, timeout=40)
        return r.json()
    except Exception as e:
        return {'error':str(e)}

@app.post('/api/analyze')
async def analyze(file: UploadFile = File(...), authorization: str = Header(None)):
    user = None
    if authorization:
        try:
            user = require_auth(authorization)
        except HTTPException:
            user = None
    content = await file.read()
    kind = file.content_type
    report = {'score':0,'verdict':'Unknown','details':{}}
    if kind.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(content)).convert('RGB')
        except Exception as e:
            return JSONResponse({'error':'Cannot open image: '+str(e)}, status_code=400)
        exif = get_exif(img); report['details']['exif']=exif
        ela = ela_score(img); blur = blur_score(img); h = phash(img)
        report['details'].update({'ela':ela,'blur_var':blur,'phash':h[0],'phash_ones':h[1]})
        score = 0.0
        score += min(40, (ela/5.0)*40)
        score += min(30, max(0,(500-blur)/500*30))
        if h[1] < 10: score += 10
        score = max(0,min(100,round(score,1)))
        report['score']=score
        if score<30: report['verdict']='Likely Genuine'
        elif score<65: report['verdict']='Suspicious / Needs Review'
        else: report['verdict']='Likely AI / Manipulated'
        # optional detectors
        if DETECTOR_TYPE=='external' and DETECTOR_API:
            files = {'file': ('upload', content)}
            report['details']['external'] = call_external(DETECTOR_API, files)
        if DETECTOR_TYPE=='hf' and HUGGINGFACE_KEY and HF_MODEL:
            report['details']['huggingface'] = call_hf(content)
    elif kind.startswith('video/'):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tmp.write(content); tmp.flush(); tmp.close()
        sz = os.path.getsize(tmp.name)/1024
        report['details']['filesize_kb']=round(sz,1); report['score']=50; report['verdict']='Video: manual review recommended'
    else:
        return JSONResponse({'error':'Unsupported file type'}, status_code=400)
    # store submission if user present
    sub_id = secrets.token_urlsafe(12)
    created = datetime.datetime.utcnow().isoformat()+'Z'
    conn = sqlite3.connect(DB_PATH); c=conn.cursor()
    uid = user['id'] if user else None
    c.execute('INSERT INTO submissions (id,user_id,filename,verdict,score,details,created_at,verified) VALUES (?,?,?,?,?,?,?,?)', (sub_id, uid, file.filename, report['verdict'], report['score'], json.dumps(report['details']), created, 0))
    conn.commit(); conn.close()
    report['submission_id']=sub_id
    return JSONResponse(report)

@app.get('/api/submissions')
def submissions(authorization: str = Header(None)):
    user = require_auth(authorization)
    conn = sqlite3.connect(DB_PATH); c=conn.cursor()
    c.execute('SELECT id,filename,verdict,score,created_at,verified FROM submissions WHERE user_id=? ORDER BY created_at DESC', (user['id'],))
    rows = c.fetchall(); conn.close()
    res = [{'id':r[0],'filename':r[1],'verdict':r[2],'score':r[3],'created_at':r[4],'verified':r[5]} for r in rows]
    return JSONResponse(res)

@app.get('/api/submission/{sid}')
def get_submission(sid: str, authorization: str = Header(None)):
    user = require_auth(authorization)
    conn = sqlite3.connect(DB_PATH); c=conn.cursor()
    c.execute('SELECT id,filename,verdict,score,details,created_at,verified FROM submissions WHERE id=?', (sid,))
    row = c.fetchone(); conn.close()
    if not row: raise HTTPException(status_code=404, detail='Not found')
    return JSONResponse({'id':row[0],'filename':row[1],'verdict':row[2],'score':row[3],'details':json.loads(row[4]),'created_at':row[5],'verified':row[6]})

@app.post('/api/verify/{sid}')
def verify_submission(sid: str, authorization: str = Header(None)):
    user = require_auth(authorization)
    conn = sqlite3.connect(DB_PATH); c=conn.cursor()
    c.execute('UPDATE submissions SET verified=1 WHERE id=?', (sid,)); conn.commit(); conn.close()
    return JSONResponse({'ok':True})

