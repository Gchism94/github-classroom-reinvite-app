from app.assignments import build_repo_name, load_assignment_records, load_assignments


def test_build_repo_name():
    assert build_repo_name("hw-01", "octocat") == "hw-01-octocat"


def test_build_repo_name_uses_assignment_prefix_and_normalized_username():
    assert build_repo_name("project-proposal", "student1") == "project-proposal-student1"


def test_load_assignments_returns_slugs_from_object_data():
    records = load_assignment_records()

    assert load_assignments() == [record["slug"] for record in records]
    assert all(isinstance(slug, str) and slug for slug in load_assignments())


def test_load_assignment_records_preserves_import_fields():
    record = load_assignment_records()[0]

    assert isinstance(record["title"], str)
    assert isinstance(record["slug"], str)
    assert "invite_link" in record
    assert "type" in record
    assert "deadline" in record
    assert "accepted" in record
    assert "submitted" in record
    assert "passing" in record
