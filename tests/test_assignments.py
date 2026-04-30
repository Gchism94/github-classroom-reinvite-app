from app.assignments import build_repo_name


def test_build_repo_name():
    assert build_repo_name("hw-01", "octocat") == "hw-01-octocat"


def test_build_repo_name_uses_assignment_prefix_and_normalized_username():
    assert build_repo_name("project-proposal", "student1") == "project-proposal-student1"
