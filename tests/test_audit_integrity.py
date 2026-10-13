from agents.base import AuditTrail


def test_tamper_detection_recomputes_signature():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("actor", "tier", "EVENT_A", {"value": 1})
    trail.log("actor", "tier", "EVENT_B", {"value": 2})
    assert trail.verify_integrity() is True
    trail.logs[0]["event_type"] = "FORGED"
    assert trail.verify_integrity() is False


def test_audit_snapshot_cannot_mutate_internal_ledger():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("actor", "tier", "EVENT", {"value": 2})
    returned = trail.get_trail()
    returned[0]["actor"] = "attacker"
    returned.clear()
    assert len(trail.get_trail()) == 1
    assert trail.verify_integrity() is True
