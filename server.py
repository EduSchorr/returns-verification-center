from fastapi import FastAPI, HTTPException

from classificador_respostas import classify_reply
from logs_db import list_cases, upsert_case
from worker_runtime import worker

app = FastAPI(title="Returns Verification Center", version="portfolio")

@app.on_event("startup")
def startup():
    worker.start()

@app.on_event("shutdown")
def shutdown():
    worker.stop()

@app.get("/api/health")
def health():
    return {"ok": True, "portfolio": True}

@app.get("/api/cases")
def cases():
    return list_cases()

@app.post("/api/classify")
def classify(payload: dict):
    case_key = str(payload.get("case_key") or "").strip()
    if not case_key:
        raise HTTPException(status_code=422, detail="case_key is required")
    result = classify_reply(str(payload.get("subject") or ""), str(payload.get("body") or ""))
    upsert_case(case_key, result.status, result.confidence, "MANUAL", result.reason)
    return result.__dict__

@app.post("/api/queue")
def queue(payload: dict):
    if not str(payload.get("case_key") or "").strip():
        raise HTTPException(status_code=422, detail="case_key is required")
    worker.submit(payload)
    return {"queued": True}
