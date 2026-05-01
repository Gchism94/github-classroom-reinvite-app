from pathlib import Path

from scripts import import_whitelist
from scripts.import_whitelist import extract_usernames


def test_extract_usernames_normalizes_validates_and_deduplicates(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "identifier,github_username,github_id,name\n"
        "1, OctoCat ,100,Octo\n"
        "2,octocat,101,Duplicate\n"
        "3,bad/name,102,Bad\n"
        "4,-bad,103,Hyphen\n"
        "5,student-1,104,Student\n"
        "6,,105,Missing\n"
    )

    result = extract_usernames(csv_path)

    assert result.usernames == ["octocat", "student-1"]
    assert result.total_rows == 6
    assert result.skipped_rows == 3
    assert result.duplicates_removed == 1


def test_extract_usernames_requires_github_username_column(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text("username,email\nMonaLisa,monalisa@example.edu\n")

    try:
        extract_usernames(csv_path)
    except ValueError as exc:
        assert "github_username" in str(exc)
    else:
        raise AssertionError("Expected missing github_username column to fail")


def test_extract_usernames_sorts_alphabetically(tmp_path: Path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "identifier,github_username,github_id,name\n"
        "1,Zebra,100,Z\n"
        "2,alpha,101,A\n"
        "3,MonaLisa,102,M\n"
    )

    result = extract_usernames(csv_path)

    assert result.usernames == ["alpha", "monalisa", "zebra"]


def test_default_roster_path_is_data_classroom_roster_csv():
    assert import_whitelist.DEFAULT_ROSTER_PATH.name == "classroom_roster.csv"
    assert import_whitelist.DEFAULT_ROSTER_PATH.parent.name == "data"


def test_custom_path_still_works(tmp_path: Path):
    csv_path = tmp_path / "custom_roster.csv"
    csv_path.write_text("identifier,github_username,github_id,name\n1,OctoCat,1,Octo\n")

    result = extract_usernames(csv_path)

    assert result.usernames == ["octocat"]


def test_example_csv_can_be_parsed():
    result = extract_usernames(Path("data/classroom_roster.example.csv"))

    assert result.usernames == ["example-student", "octocat"]
    assert result.total_rows == 2
