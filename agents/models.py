"""
Pydantic v2 schemas and data definitions for Rna Secondary Structure Vienna.
Domain: AI Drug Discovery, Structural Biology & Wet-Lab Robotics
Standard: wwPDB / IUPAC / OpenSMILES / ISAC Standards
"""
import datetime
import math
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier", max_length=128)
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target", max_length=128)
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor", max_length=64)
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier")
    @classmethod
    def validate_safe_identifier(cls, v: str) -> str:
        """Prevent path traversal and injection via identifiers."""
        if not v or not v.strip():
            raise ValueError("Identifier must not be empty or whitespace")
        if any(c in v for c in ['..', '/', '\\', '\x00', '\n', '\r']):
            raise ValueError(f"Identifier contains unsafe characters: {v!r}")
        return v.strip()

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_finite_metric(cls, v: float) -> float:
        """Reject NaN and infinite values."""
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise ValueError(f"Metric value must be finite, got {v}")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "wwPDB / IUPAC / OpenSMILES / ISAC Standards"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "rna-secondary-structure-vienna"
    domain: str = "AI Drug Discovery, Structural Biology & Wet-Lab Robotics"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "wwPDB / IUPAC / OpenSMILES / ISAC Standards"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
