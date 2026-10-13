"""
FastAPI REST API Server for Rna Secondary Structure Vienna.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from rna_shape_predictor.folding import FoldingUnavailableError, fold_rna

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Rna Secondary Structure Vienna API",
    description="Enterprise Distributed Component Platform (AI Drug Discovery, Structural Biology & Wet-Lab Robotics)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "rna-secondary-structure-vienna", "domain": "AI Drug Discovery, Structural Biology & Wet-Lab Robotics", "standard": "wwPDB / IUPAC / OpenSMILES / ISAC Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


class FoldRequest(BaseModel):
    sequence: str


@app.post("/api/fold")
def api_fold(req: FoldRequest):
    """Compute ViennaRNA MFE, not the separate browser Nussinov approximation."""
    try:
        return fold_rna(req.sequence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FoldingUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
