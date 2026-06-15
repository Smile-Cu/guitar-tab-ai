import sys
sys.path.insert(0, r"C:\Users\l'l\AppData\Local\Programs\Python\Python312\Lib\site-packages")
sys.path.insert(1, r"D:\guitar-tab-ai\backend\python-packages")

import tab_converter, database
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, tempfile, traceback, shutil

AI_AVAILABLE = False
try:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    from basic_pitch.inference import predict
    from basic_pitch import FilenameSuffix, build_icassp_2022_model_path
    ONNX_MODEL_PATH = str(build_icassp_2022_model_path(FilenameSuffix.onnx))
    AI_AVAILABLE = True
except Exception:
    pass

OUTPUT_DIR = tempfile.mkdtemp(prefix="guitartab_")
GUITAR_MIN_PITCH, GUITAR_MAX_PITCH, MIN_NOTE_DURATION = 36, 84, 0.08
MAX_NOTES = 80

def filter_guitar_notes(raw_notes):
    total = len(raw_notes)
    filtered = []
    for n in raw_notes:
        p, dur = int(n[2]), float(n[1]) - float(n[0])
        if p < GUITAR_MIN_PITCH or p > GUITAR_MAX_PITCH: continue
        if dur < MIN_NOTE_DURATION: continue
        filtered.append({"pitch": p, "start_time": round(float(n[0]), 2), "end_time": round(float(n[1]), 2)})
    if len(filtered) > MAX_NOTES:
        filtered.sort(key=lambda n: n["end_time"] - n["start_time"], reverse=True)
        filtered = filtered[:MAX_NOTES]
        filtered.sort(key=lambda n: n["start_time"])
    print(f"[Filter] {total} -> {len(filtered)} notes")
    return filtered


def get_token(request: Request):
    auth = request.headers.get("Authorization", "")
    return auth[7:] if auth.startswith("Bearer ") else None


app = FastAPI(title="GuitarTab AI")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def handler(request, exc):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": str(exc)})

@app.get("/")
def root():
    return {"status": "ok", "ai_available": AI_AVAILABLE}

@app.post("/api/register")
async def register(body: dict):
    u, p = body.get("username", "").strip(), body.get("password", "")
    if not u or not p or len(p) < 3:
        return JSONResponse(status_code=400, content={"error": "用户名和密码至少3位"})
    try:
        db = database.get_db()
        db.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, datetime('now'))", (u, database.hash_password(p)))
        db.commit()
        uid = db.execute("SELECT id FROM users WHERE username = ?", (u,)).fetchone()["id"]
        token = database.create_token(uid)
        db.close()
        return {"token": token, "username": u}
    except Exception:
        return JSONResponse(status_code=400, content={"error": "用户名已存在"})

@app.post("/api/login")
async def login(body: dict):
    u, p = body.get("username", "").strip(), body.get("password", "")
    db = database.get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (u,)).fetchone()
    db.close()
    if not row or row["password_hash"] != database.hash_password(p):
        return JSONResponse(status_code=401, content={"error": "用户名或密码错误"})
    return {"token": database.create_token(row["id"]), "username": u}

@app.post("/api/tabs")
async def save_tab(body: dict, request: Request):
    token = get_token(request)
    uid = database.verify_token(token) if token else None
    if not uid: return JSONResponse(status_code=401, content={"error": "请先登录"})
    db = database.get_db()
    db.execute("INSERT INTO tabs (user_id, filename, tab_text, note_count, mode, created_at) VALUES (?,?,?,?,?,datetime('now'))",
               (uid, body.get("filename",""), body.get("tab_text",""), body.get("note_count",0), body.get("mode","")))
    db.commit()
    tid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return {"id": tid, "saved": True}

@app.get("/api/tabs")
async def list_tabs(request: Request):
    token = get_token(request)
    uid = database.verify_token(token) if token else None
    if not uid: return JSONResponse(status_code=401, content={"error": "请先登录"})
    db = database.get_db()
    rows = db.execute("SELECT id, filename, note_count, mode, created_at FROM tabs WHERE user_id=? ORDER BY created_at DESC", (uid,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.delete("/api/tabs/{tab_id}")
async def delete_tab(tab_id: int, request: Request):
    token = get_token(request)
    uid = database.verify_token(token) if token else None
    if not uid: return JSONResponse(status_code=401, content={"error": "请先登录"})
    db = database.get_db()
    db.execute("DELETE FROM tabs WHERE id=? AND user_id=?", (tab_id, uid))
    db.commit(); db.close()
    return {"deleted": True}

@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    allowed = (".wav",".mp3",".ogg",".flac",".m4a")
    if not file.filename or not any(file.filename.lower().endswith(e) for e in allowed):
        return JSONResponse(status_code=400, content={"error": "仅支持 wav/mp3/ogg/flac/m4a"})
    content = await file.read()
    fname = file.filename or "unknown"
    if len(content) < 100: return JSONResponse(status_code=400, content={"error":"文件过小"})

    def _r(notes, fn, m="ai"):
        fp, dn = tab_converter.generate_midi_from_notes(notes)
        d = os.path.join(OUTPUT_DIR, dn)
        shutil.copy2(fp, d); os.unlink(fp)
        return {"filename":fn,"mode":m,"midi_file":dn,"download_url":f"/api/download/{dn}",
                "note_count":len(notes),"tab_text":tab_converter.create_tab_text(notes)}

    if not AI_AVAILABLE: return _r(tab_converter.get_mock_notes(), fname, m="mock")
    import tempfile as tf; tmp = None
    try:
        with tf.NamedTemporaryFile(suffix=".wav", delete=False) as t:
            t.write(content); tmp = t.name
        _, _, ne = predict(tmp, model_or_model_path=ONNX_MODEL_PATH)
        return _r(filter_guitar_notes(ne), fname)
    except Exception as e:
        r = _r(tab_converter.get_mock_notes(), fname)
        r["mode"] = "mock (AI fallback)"; r["error"] = str(e)
        return r
    finally:
        if tmp: os.unlink(tmp)

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    fp = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(fp): raise __import__("fastapi").HTTPException(status_code=404)
    return FileResponse(path=fp, filename=filename, media_type="audio/midi")
@app.get("/api/tabs/{tab_id}")
async def get_tab(tab_id: int, request: Request):
    token = get_token(request)
    uid = database.verify_token(token) if token else None
    if not uid: return JSONResponse(status_code=401, content={"error": "请先登录"})
    db = database.get_db()
    row = db.execute("SELECT * FROM tabs WHERE id = ? AND user_id = ?", (tab_id, uid)).fetchone()
    db.close()
    if not row: return JSONResponse(status_code=404, content={"error": "未找到"})
    return dict(row)
