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
    from basic_pitch import ICASSP_2022_MODEL_PATH, FilenameSuffix, build_icassp_2022_model_path

    # SavedModel 格式在 TF 2.21 下有兼容性问题，改用 TFLite
    TFLITE_MODEL_PATH = str(build_icassp_2022_model_path(FilenameSuffix.tflite))

    AI_AVAILABLE = True
    print(f"[AI 模式] basic-pitch + librosa 已加载 (TFLite)")
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
        "message": "GuitarTab AI 后端运行中",
    }


def _mock_result(filename: str, size_bytes: int):
    mock_notes = tab_converter.get_mock_notes()
    converted = tab_converter.convert_notes_to_tab(mock_notes)
    tab_text = tab_converter.format_tab_string(converted)
    return {
        "filename": filename,
        "size_bytes": size_bytes,
        "mode": "mock",
        "notes": converted,
        "tab_text": tab_text,
    }


@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    allowed = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
    if not file.filename or not any(
        file.filename.lower().endswith(ext) for ext in allowed
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="仅支持 wav/mp3/ogg/flac/m4a")

    content = await file.read()
    fname = file.filename or "unknown"
    fsize = len(content)

    if not AI_AVAILABLE:
        return _mock_result(fname, fsize)

    import tempfile
    import os
    import traceback

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # 使用 TFLite 模型路径，避免 SavedModel 兼容性问题
        model_output, midi_data, note_events = predict(
            tmp_path, model_or_model_path=TFLITE_MODEL_PATH
        )

        notes = []
        for n in note_events:
            notes.append({
                "pitch": int(n.pitch),
                "start_time": round(float(n.start_time_s), 2),
                "end_time": round(float(n.end_time_s), 2),
            })

        converted_notes = tab_converter.convert_notes_to_tab(notes)
        tab_text = tab_converter.format_tab_string(converted_notes)

        return {
            "filename": fname,
            "size_bytes": fsize,
            "mode": "ai",
            "notes": converted_notes,
            "tab_text": tab_text,
        }

    except Exception as e:
        print(f"[AI 推理失败，降级为模拟模式] {e}")
        traceback.print_exc()
        result = _mock_result(fname, fsize)
        result["mode"] = "mock (AI 降级)"
        result["error"] = str(e)
        return result

    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
