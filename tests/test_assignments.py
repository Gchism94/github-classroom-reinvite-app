from app.assignments import build_repo_name, load_assignment_records, load_assignments


def test_build_repo_name():
    assert build_repo_name("hw-01", "octocat") == "hw-01-octocat"


def test_build_repo_name_uses_assignment_prefix_and_normalized_username():
    assert build_repo_name("project-proposal", "student1") == "project-proposal-student1"


def test_load_assignments_returns_slugs_from_object_data():
    assert load_assignments() == ["hw-01", "hw-02", "project-proposal"]


def test_load_assignment_records_preserves_import_fields():
    record = load_assignment_records()[0]

    assert record["title"] == "Homework 01"
    assert record["slug"] == "hw-01"
    assert "invite_link" in record
    assert "deadline" in record
