import json
from pathlib import Path

from app.audit import append_audit_log


def test_append_audit_log_writes_safe_json_line(tmp_path: Path):
    audit_path = tmp_path / "audit.log"

    append_audit_log(
        username="octocat",
        assignment="hw-01",
        repo="hw-01-octocat",
        status="success",
        github_http_status=201,
        message="Invitation created.",
        path=audit_path,
    )

    entry = json.loads(audit_path.read_text().strip())

    assert entry["username"] == "octocat"
    assert entry["assignment"] == "hw-01"
    assert entry["repo"] == "hw-01-octocat"
    assert entry["status"] == "success"
    assert entry["github_http_status"] == 201
    assert entry["message"] == "Invitation created."
    assert "timestamp" in entry
    assert "token" not in entry
    assert "private_key" not in entry
