from pathlib import Path

from app.auth import is_authorized, load_whitelist


def test_load_whitelist_normalizes_usernames(tmp_path: Path):
    whitelist_file = tmp_path / "whitelist.json"
    whitelist_file.write_text('[" OctoCat ", "STUDENT-1"]')

    assert load_whitelist(whitelist_file) == {"octocat", "student-1"}


def test_is_authorized_checks_normalized_username():
    assert is_authorized(" OctoCat ", {"octocat"})
    assert not is_authorized("other-user", {"octocat"})
