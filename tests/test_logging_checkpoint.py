from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app
from app.pii import hash_user_id


CORRELATION_ID_PATTERN = re.compile(r"^req-[0-9a-f]{8}$")


def _post_chat(client: TestClient, message: str, **headers: str):
    return client.post(
        "/chat",
        headers=headers,
        json={
            "user_id": "student-01",
            "session_id": "session-01",
            "feature": "qa",
            "message": message,
        },
    )


def test_chat_logs_have_correlation_and_enrichment(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = _post_chat(client, "Explain observability")

    correlation_id = response.headers["x-request-id"]
    assert response.status_code == 200
    assert response.json()["correlation_id"] == correlation_id
    assert CORRELATION_ID_PATTERN.fullmatch(correlation_id)
    assert float(response.headers["x-response-time-ms"]) >= 0

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    for record in api_records:
        assert record["correlation_id"] == correlation_id
        assert record["user_id_hash"] == hash_user_id("student-01")
        assert record["session_id"] == "session-01"
        assert record["feature"] == "qa"
        assert record["model"]
        assert record["env"]


def test_invalid_request_id_is_replaced_and_valid_one_is_propagated(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")

    with TestClient(app) as client:
        replaced = _post_chat(client, "First", **{"x-request-id": "not-valid"})
        propagated = _post_chat(client, "Second", **{"x-request-id": "req-A1B2C3D4"})

    assert CORRELATION_ID_PATTERN.fullmatch(replaced.headers["x-request-id"])
    assert replaced.headers["x-request-id"] != "not-valid"
    assert propagated.headers["x-request-id"] == "req-a1b2c3d4"


def test_raw_pii_does_not_reach_json_log(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    raw_values = (
        "student@vinuni.edu.vn",
        "090 123 4567",
        "4111 1111 1111 1111",
    )

    with TestClient(app) as client:
        for value in raw_values:
            assert _post_chat(client, f"Sensitive test value: {value}").status_code == 200

    raw_log = log_path.read_text(encoding="utf-8")
    for value in raw_values:
        assert value not in raw_log
    assert "[REDACTED_EMAIL]" in raw_log
    assert "[REDACTED_PHONE_VN]" in raw_log
    assert "[REDACTED_CREDIT_CARD]" in raw_log
