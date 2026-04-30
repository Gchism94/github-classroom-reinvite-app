from app.github_client import CollaboratorResult, GitHubClientError
from scripts import batch_reinvite, validate_repos


def test_validate_repos_dry_run_builds_expected_repo_matrix(monkeypatch):
    monkeypatch.setattr(validate_repos, "get_assignment_slugs", lambda assignment: ["hw-01"])
    monkeypatch.setattr(validate_repos, "get_whitelisted_usernames", lambda: ["octocat", "student-1"])

    report = validate_repos.validate_repos("hw-01", dry_run=True)

    assert report["summary"]["total_checked"] == 2
    assert report["summary"]["dry_run"] is True
    assert report["entries"][0]["repo"] == "hw-01-octocat"
    assert report["entries"][1]["repo"] == "hw-01-student-1"
    assert all(entry["status"] == "dry_run" for entry in report["entries"])


def test_batch_reinvite_dry_run_appends_audit_without_github(monkeypatch):
    audit_entries = []
    monkeypatch.setattr(batch_reinvite, "get_assignment_slugs", lambda assignment: ["hw-01"])
    monkeypatch.setattr(batch_reinvite, "get_whitelisted_usernames", lambda limit: ["octocat"])
    monkeypatch.setattr(batch_reinvite, "append_audit_log", lambda **entry: audit_entries.append(entry))
    monkeypatch.setattr(batch_reinvite, "add_collaborator", lambda repo, username: (_ for _ in ()).throw(AssertionError("should not call GitHub")))

    report = batch_reinvite.batch_reinvite("hw-01", dry_run=True)

    assert report["summary"]["total_attempted"] == 1
    assert report["entries"][0]["status"] == "dry_run"
    assert audit_entries[0]["repo"] == "hw-01-octocat"


def test_batch_reinvite_classifies_success_and_already_access(monkeypatch):
    calls = []
    audit_entries = []
    monkeypatch.setattr(batch_reinvite, "get_assignment_slugs", lambda assignment: ["hw-01"])
    monkeypatch.setattr(batch_reinvite, "get_whitelisted_usernames", lambda limit: ["octocat", "student-1"])
    monkeypatch.setattr(batch_reinvite, "append_audit_log", lambda **entry: audit_entries.append(entry))

    def fake_add_collaborator(repo, username):
        calls.append((repo, username))
        if username == "octocat":
            return CollaboratorResult("Invitation created.", 201)
        return CollaboratorResult("Write access already active.", 204)

    monkeypatch.setattr(batch_reinvite, "add_collaborator", fake_add_collaborator)
    monkeypatch.setattr(batch_reinvite, "save_report", lambda path, report: None)

    report = batch_reinvite.batch_reinvite("hw-01")

    assert calls == [("hw-01-octocat", "octocat"), ("hw-01-student-1", "student-1")]
    assert report["summary"]["successes"] == 2
    assert report["summary"]["invitation_created"] == 1
    assert report["summary"]["already_had_access"] == 1
    assert [entry["status"] for entry in audit_entries] == [
        "invitation_created",
        "already_had_access",
    ]


def test_batch_reinvite_classifies_missing_and_permission_errors(monkeypatch):
    audit_entries = []
    monkeypatch.setattr(batch_reinvite, "get_assignment_slugs", lambda assignment: ["hw-01"])
    monkeypatch.setattr(batch_reinvite, "get_whitelisted_usernames", lambda limit: ["octocat", "student-1"])
    monkeypatch.setattr(batch_reinvite, "append_audit_log", lambda **entry: audit_entries.append(entry))
    monkeypatch.setattr(batch_reinvite, "save_report", lambda path, report: None)

    def fake_add_collaborator(repo, username):
        if username == "octocat":
            raise GitHubClientError(404, "Missing.", github_http_status=404)
        raise GitHubClientError(403, "Permission.", github_http_status=403)

    monkeypatch.setattr(batch_reinvite, "add_collaborator", fake_add_collaborator)

    report = batch_reinvite.batch_reinvite("hw-01")

    assert report["summary"]["missing_repos"] == 1
    assert report["summary"]["permission_issues"] == 1
    assert [entry["status"] for entry in audit_entries] == [
        "missing",
        "permission_issue",
    ]
