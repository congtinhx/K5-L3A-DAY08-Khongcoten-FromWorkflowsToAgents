"""Extra tests for Shape C (orchestrator). Owner: Nguoi 3.

- Trace and handoff must not contain CANARY_SECRET_ or parent_secret.
- Investigators must not receive write tools.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import get_refund
from lab8.handoff import HandoffError, make_handoff
from lab8.runtime import ToolRejected, dispatch
from lab8.schemas import Budget
from lab8.shapes.orchestrator import run_claim


def _trace_body(result) -> dict:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))


def test_trace_no_canary_secret(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    body = _trace_body(result)
    blob = json.dumps(body, ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob


def test_trace_no_canary_secret_all_claims(public_db):
    for claim_id in ["C-001", "C-003", "C-005", "C-010"]:
        result = run_claim(claim_id, seed=22, store_path=str(public_db))
        blob = json.dumps(_trace_body(result), ensure_ascii=False)
        assert "CANARY_SECRET_" not in blob, f"{claim_id}: trace contains CANARY_SECRET_"
        assert "parent_secret" not in blob, f"{claim_id}: trace contains parent_secret"


def test_handoff_no_write_tools():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-TEST",
            claim_id="C-001",
            task="pay",
            facts={},
            allowed_tools=["issue_refund"],
        )


def test_investigator_cannot_call_write_tool(public_db):
    conn = connect(public_db)
    budget = Budget()
    with pytest.raises(ToolRejected):
        dispatch(conn, budget, "issue_refund", {"claim_id": "C-001"}, worker=True)
    conn.close()


def test_investigator_cannot_call_append_audit(public_db):
    conn = connect(public_db)
    budget = Budget()
    with pytest.raises(ToolRejected):
        dispatch(conn, budget, "append_audit", {"claim_id": "C-001"}, worker=True)
    conn.close()


def test_trace_has_run_id_and_events(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    body = _trace_body(result)
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)
    assert len(body["events"]) > 0


def test_early_return_needs_info_still_has_trace(public_db):
    # C-004 has no order_id — shape returns needs_info early
    result = run_claim("C-004", seed=11, store_path=str(public_db))
    assert result.status == "needs_info"
    body = _trace_body(result)
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)
    blob = json.dumps(body, ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob


def test_escalated_no_refund_no_secret(public_db):
    # C-005: P-200 trying to access O-110 owned by P-100 → escalated
    result = run_claim("C-005", seed=11, store_path=str(public_db))
    assert result.status == "escalated"
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-005") is None
    finally:
        conn.close()
    blob = json.dumps(_trace_body(result), ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob


def test_handoff_sanitize_drops_parent_secret():
    from lab8.handoff import sanitize
    payload = {
        "contract_version": "handoff.v1",
        "request_id": "REQ-X",
        "claim_id": "C-010",
        "principal_scope": "owner_order_only",
        "task": "check_applicable_policy",
        "facts": {},
        "allowed_tools": ["lookup_policy"],
        "max_output_tokens": 400,
        "parent_secret": "CANARY_SECRET_PARENT_X",
        "raw_headers": {"Authorization": "Bearer CANARY_SECRET_PARENT_X"},
    }
    cleaned = sanitize(payload)
    blob = json.dumps(cleaned, ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in cleaned
