from app.classroom_client import (
    build_accepted_assignments_payload,
    normalize_accepted_assignment,
    normalize_classroom_assignment,
)
from scripts import sync_classroom


def test_normalize_classroom_assignment_keeps_required_import_fields():
    raw = {
        "id": 123,
        "title": "Homework 03",
        "slug": "hw-03",
        "invite_link": "https://classroom.github.com/a/example",
        "deadline": "2026-05-01T23:59:00Z",
        "extra": "ignored",
    }

    assert normalize_classroom_assignment(raw) == {
        "id": 123,
        "title": "Homework 03",
        "slug": "hw-03",
        "invite_link": "https://classroom.github.com/a/example",
        "deadline": "2026-05-01T23:59:00Z",
    }


def test_normalize_accepted_assignment_keeps_student_and_repo_metadata():
    raw = {
        "id": 456,
        "submitted": True,
        "passing": False,
        "commit_count": 8,
        "grade": "8/10",
        "students": [
            {"id": 1, "login": "octocat", "html_url": "https://github.com/octocat"}
        ],
        "repository": {
            "id": 789,
            "full_name": "course/hw-03-octocat",
            "html_url": "https://github.com/course/hw-03-octocat",
            "private": True,
            "default_branch": "main",
        },
    }

    accepted = normalize_accepted_assignment(raw)

    assert accepted["students"] == [
        {"id": 1, "login": "octocat", "html_url": "https://github.com/octocat"}
    ]
    assert accepted["repository"]["full_name"] == "course/hw-03-octocat"


def test_build_accepted_assignments_payload_groups_by_assignment_id():
    assignments = [
        {
            "id": 123,
            "title": "Homework 03",
            "slug": "hw-03",
            "invite_link": None,
            "deadline": None,
        }
    ]
    accepted = {"123": [{"id": 456}]}

    payload = build_accepted_assignments_payload(assignments, accepted, "999")

    assert payload["classroom_id"] == "999"
    assert payload["assignments"][0]["assignment_id"] == 123
    assert payload["assignments"][0]["slug"] == "hw-03"
    assert payload["assignments"][0]["accepted_assignments"] == [{"id": 456}]


def test_sync_classroom_dry_run_does_not_save(monkeypatch):
    class FakeClient:
        def __init__(self, settings):
            pass

        def list_assignments(self, classroom_id):
            return [
                {
                    "id": 123,
                    "title": "Homework 03",
                    "slug": "hw-03",
                    "invite_link": None,
                    "deadline": None,
                }
            ]

        def list_accepted_assignments(self, assignment_id):
            return []

    monkeypatch.setattr(sync_classroom, "get_settings", lambda: type("Settings", (), {"github_classroom_id": "999"})())
    monkeypatch.setattr(sync_classroom, "GitHubClassroomClient", FakeClient)
    monkeypatch.setattr(sync_classroom, "save_assignments", lambda assignments: (_ for _ in ()).throw(AssertionError("should not save assignments")))
    monkeypatch.setattr(sync_classroom, "save_accepted_assignments", lambda payload: (_ for _ in ()).throw(AssertionError("should not save accepted assignments")))

    sync_classroom.sync_classroom(None, dry_run=True)
