import tab_converter

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# ----- 检测 AI 依赖是否可用 -----
AI_AVAILABLE = False
try:
    import sys
    sys.path.insert(0, r"D:\guitar-tab-ai\backend\python-packages")
 
    import librosa
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    AI_AVAILABLE = True
    print("[AI 模式] basic-pitch + librosa 已加载")
except ImportError as e:
    print(f"[模拟模式] AI 依赖未安装，使用模拟数据 (原因: {e})")


# ----- FastAPI 应用 -----
app = FastAPI(title="GuitarTab AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "ai_available": AI_AVAILABLE,
        "message": "GuitarTab AI 后端运行中"
    }


@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    # 校验文件格式
    allowed = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
    if not file.filename or not any(
        file.filename.lower().endswith(ext) for ext in allowed
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="仅支持 wav/mp3/ogg/flac/m4a")

    content = await file.read()

    if not AI_AVAILABLE:
        # 模拟模式：返回示例音符数据
        return {
            "filename": file.filename,
            "size_bytes": len(content),
            "mode": "mock",
            "notes": [
                {"pitch": 64, "start_time": 0.0, "end_time": 0.5},
                {"pitch": 67, "start_time": 0.5, "end_time": 1.0},
                {"pitch": 71, "start_time": 1.0, "end_time": 1.5},
            ]
        }

    # AI 模式：真实推理
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        model_output, midi_data, note_events = predict(tmp_path)
        notes = []
        for n in note_events:
            notes.append({
                "pitch": int(n.pitch),
                "start_time": round(float(n.start_time_s), 2),
                "end_time": round(float(n.end_time_s), 2),
            })
        converted_notes = tab_converter.convert_notes_to_tab(notes)
        return {"filename": file.filename, "size_bytes": len(content), "mode": "ai", "notes": converted_notes}
    finally:
        os.unlink(tmp_path)
