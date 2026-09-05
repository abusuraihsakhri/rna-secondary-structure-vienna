"""
Security and input validation tests for rna-secondary-structure-vienna.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import math
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestInputValidation:
    """Tests for input validation on SystemTaskPayload."""

    def test_valid_payload(self):
        """Normal valid payload should be accepted."""
        p = SystemTaskPayload(task_id="TASK-01", target_identifier="TARGET-01", primary_metric=10.0)
        assert p.task_id == "TASK-01"
        assert p.primary_metric == 10.0

    def test_empty_task_id_rejected(self):
        """Empty task_id should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="", target_identifier="T1", primary_metric=1.0)

    def test_whitespace_task_id_rejected(self):
        """Whitespace-only task_id should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="   ", target_identifier="T1", primary_metric=1.0)

    def test_path_traversal_task_id_rejected(self):
        """Path traversal patterns in task_id should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="../etc/passwd", target_identifier="T1", primary_metric=1.0)

    def test_path_traversal_target_rejected(self):
        """Path traversal patterns in target_identifier should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="T1", target_identifier="..\\windows\\system32", primary_metric=1.0)

    def test_nan_metric_rejected(self):
        """NaN metric values should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="T1", target_identifier="TGT-01", primary_metric=float('nan'))

    def test_inf_metric_rejected(self):
        """Infinite metric values should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="T1", target_identifier="TGT-01", primary_metric=float('inf'))

    def test_task_id_stripped(self):
        """Task ID should be stripped of leading/trailing whitespace."""
        p = SystemTaskPayload(task_id="  TASK-01  ", target_identifier="T1", primary_metric=1.0)
        assert p.task_id == "TASK-01"

    def test_max_length_enforced(self):
        """Task ID exceeding max length should be rejected."""
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="X" * 200, target_identifier="T1", primary_metric=1.0)


class TestPHIGuard:
    """Tests for PHI outbound guard."""

    def test_mrn_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_ssn_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_email_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact patient@hospital.com for results")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_text_passes(self):
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 has results")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN-12345678" not in result


class TestAuditTrailSecurity:
    """Tests for audit trail security features."""

    def test_random_key_generated_when_no_env(self):
        """AuditTrail should generate a random key when no secret is provided."""
        trail = AuditTrail(secret_key="test-key-for-unit-test")
        assert len(trail.secret_key) > 0

    def test_audit_integrity_verification(self):
        """Audit trail should verify integrity of chained entries."""
        trail = AuditTrail(secret_key="integrity-test-key")
        trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_not_empty_after_log(self):
        """Audit trail should contain entries after logging."""
        trail = AuditTrail(secret_key="nonempty-test-key")
        assert len(trail.get_trail()) == 0
        trail.log("actor", "tier", "EVENT", {})
        assert len(trail.get_trail()) == 1


class TestSupervisorWithValidation:
    """Tests supervisor with validated inputs."""

    def test_process_valid_task(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="VALID-TASK-01",
            target_identifier="VALID-TARGET-01",
            primary_metric=10.0,
            secondary_metric=5.0,
            status_descriptor="NOMINAL"
        )
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE
        assert dossier.audit_hash != ""

    def test_supervisor_blocks_phi_in_task_id(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="TASK-01",
            target_identifier="MRN-12345678",
            primary_metric=10.0,
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)
