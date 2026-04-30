from app.assignments import build_repo_name


def test_build_repo_name():
    assert build_repo_name("hw-01", "octocat") == "hw-01-octocat"
