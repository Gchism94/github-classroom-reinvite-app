from pathlib import Path

from scripts.import_whitelist import extract_usernames


def test_extract_usernames_normalizes_validates_and_deduplicates(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "name,github_username\n"
        "Octo, OctoCat \n"
        "Duplicate,octocat\n"
        "Bad,bad/name\n"
        "Hyphen,-bad\n"
        "Student,student-1\n"
    )

    usernames, rejected = extract_usernames(csv_path, "github_username")

    assert usernames == ["octocat", "student-1"]
    assert rejected == ["bad/name", "-bad"]


def test_extract_usernames_falls_back_to_first_column(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text("username,email\nMonaLisa,monalisa@example.edu\n")

    usernames, rejected = extract_usernames(csv_path, "github_username")

    assert usernames == ["monalisa"]
    assert rejected == []


def test_extract_usernames_matches_header_case_insensitively(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text("Name,GitHub_Username\nStudent,OctoCat\n")

    usernames, rejected = extract_usernames(csv_path, "github_username")

    assert usernames == ["octocat"]
    assert rejected == []
