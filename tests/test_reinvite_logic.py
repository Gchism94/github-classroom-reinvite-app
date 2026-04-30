import pytest
from fastapi import HTTPException

from app.routes import reinvite as reinvite_route


def test_reinvite_constructs_repo_and_calls_github(monkeypatch):
    monkeypatch.setattr(reinvite_route, "load_assignments", lambda: ["hw-03"])
    monkeypatch.setattr(reinvite_route, "is_authorized", lambda username: True)
    calls = []

    def fake_add_collaborator(repo_name, username):
        calls.append((repo_name, username))
        return "Invitation created."

    response = reinvite_route.reinvite_user(
        "GChism", "hw-03", add_collaborator_func=fake_add_collaborator
    )

    assert response.repo == "hw-03-gchism"
    assert response.status == "Invitation created."
    assert calls == [("hw-03-gchism", "gchism")]


def test_reinvite_rejects_non_whitelisted_user_before_github(monkeypatch):
    monkeypatch.setattr(reinvite_route, "load_assignments", lambda: ["hw-03"])
    monkeypatch.setattr(reinvite_route, "is_authorized", lambda username: False)

    def fail_if_called(repo_name, username):
        raise AssertionError("GitHub should not be called for non-whitelisted users")

    with pytest.raises(HTTPException) as exc:
        reinvite_route.reinvite_user(
            "octocat", "hw-03", add_collaborator_func=fail_if_called
        )

    assert exc.value.status_code == 403


def test_reinvite_rejects_invalid_assignment(monkeypatch):
    monkeypatch.setattr(reinvite_route, "load_assignments", lambda: ["hw-03"])
    monkeypatch.setattr(reinvite_route, "is_authorized", lambda username: True)

    with pytest.raises(HTTPException) as exc:
        reinvite_route.reinvite_user(
            "octocat",
            "hw-04",
            add_collaborator_func=lambda repo_name, username: "should not happen",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid assignment."
