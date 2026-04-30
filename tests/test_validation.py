from app.validation import is_valid_github_username, normalize_username


def test_normalize_username():
    assert normalize_username(" OctoCat ") == "octocat"


def test_valid_github_username():
    assert is_valid_github_username("octocat")
    assert is_valid_github_username("student-1")
    assert is_valid_github_username("A" * 39)


def test_invalid_github_username():
    assert not is_valid_github_username("-bad")
    assert not is_valid_github_username("bad-")
    assert not is_valid_github_username("bad/name")
    assert not is_valid_github_username("")
    assert not is_valid_github_username("a" * 40)
