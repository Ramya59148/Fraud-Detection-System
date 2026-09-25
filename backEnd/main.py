import os
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Query,
    Depends,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import (
    get_history,
    get_scan_by_id,
    delete_scan,
    clear_history,
    get_dashboard_stats
)
from .schemas import (
    TextInput,
    EmailInput,
    UrlInput,
    ScanResponse,
    HistoryResponse,
    DashboardStatsResponse,
    SystemStatusResponse
)
from .ml_engine.model_manager import ModelManager
from .ml_engine.verdict_engine import VerdictEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload ML models during server startup
    print("=" * 60)
    print("SENTRIX AI FRAUD DETECTION SYSTEM - BOOTING BACKEND")
    print("=" * 60)
    try:
        ModelManager.get_instance()
        print("[Sentrix API] All AI/ML models loaded and online.")
    except Exception as e:
        print(f"[Sentrix API] Warning loading models during startup: {e}")
    yield
    print("[Sentrix API] Shutting down.")


app = FastAPI(
    title="Sentrix AI Fraud Detection API",
    description="Multi-modal AI-powered Cybersecurity and Threat Detection Platform",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for local development and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    return {
        "name": "Sentrix AI Fraud Detection Platform",
        "version": "2.0.0",
        "status": "OPERATIONAL",
        "docs_url": "/docs"
    }


@app.get("/api/health", tags=["Telemetry"])
async def health_check():
    mm = ModelManager.get_instance()
    return {
        "status": "HEALTHY",
        "device": str(mm.device),
        "models_loaded": {
            "text_model": mm.text_model is not None,
            "email_model": mm.email_model is not None,
            "url_model": mm.url_rf_model is not None
        }
    }


@app.get("/api/models/status", response_model=SystemStatusResponse, tags=["Telemetry"])
async def models_status():
    mm = ModelManager.get_instance()
    info = mm.get_status()
    return {
        "status": "OPERATIONAL",
        "models": info["models"],
        "device": info["device"]
    }


@app.get("/api/stats", response_model=DashboardStatsResponse, tags=["Telemetry"])
async def get_stats():
    return get_dashboard_stats()


# ==========================================
# SCANNING ENDPOINTS
# ==========================================

@app.post("/api/scan/text", response_model=ScanResponse, tags=["Scanners"])
async def scan_text(payload: TextInput):
    try:
        result = VerdictEngine.process_text_scan(
            text=payload.text,
            title=payload.title
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text analysis failed: {str(e)}"
        )


@app.post("/api/scan/email", response_model=ScanResponse, tags=["Scanners"])
async def scan_email(payload: EmailInput):
    try:
        result = VerdictEngine.process_email_scan(
            body=payload.body,
            subject=payload.subject,
            sender=payload.sender
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email analysis failed: {str(e)}"
        )


@app.post("/api/scan/url", response_model=ScanResponse, tags=["Scanners"])
async def scan_url(payload: UrlInput):
    try:
        result = VerdictEngine.process_url_scan(url=payload.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL threat analysis failed: {str(e)}"
        )


@app.post("/api/scan/file", response_model=ScanResponse, tags=["Scanners"])
async def scan_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename or "unknown.dat"
        result = VerdictEngine.process_file_scan(
            filename=filename,
            content_bytes=content
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File inspection failed: {str(e)}"
        )


@app.post("/api/scan/audio", response_model=ScanResponse, tags=["Scanners"])
async def scan_audio(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename or "audio_recording.wav"
        result = VerdictEngine.process_audio_scan(
            audio_bytes=content,
            filename=filename
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio deepfake analysis failed: {str(e)}"
        )


# ==========================================
# HISTORY ENDPOINTS
# ==========================================

@app.get("/api/history", response_model=HistoryResponse, tags=["History"])
async def get_scan_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    input_type: Optional[str] = Query(None),
    verdict: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    return get_history(
        limit=limit,
        offset=offset,
        input_type=input_type,
        verdict=verdict,
        search=search
    )


@app.get("/api/history/{scan_id}", response_model=ScanResponse, tags=["History"])
async def get_scan_details(scan_id: str):
    record = get_scan_by_id(scan_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record '{scan_id}' not found."
        )
    return record


@app.delete("/api/history/{scan_id}", tags=["History"])
async def remove_scan_record(scan_id: str):
    success = delete_scan(scan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record '{scan_id}' not found."
        )
    return {"message": f"Scan '{scan_id}' deleted successfully."}


@app.delete("/api/history", tags=["History"])
async def clear_all_history():
    count = clear_history()
    return {"message": f"Cleared {count} scan records."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backEnd.main:app", host="127.0.0.1", port=8000, reload=True)
