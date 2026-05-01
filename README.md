# GitHub Classroom Reinvite App (Template)

![CI](https://github.com/Gchism94/github-classroom-reinvite-app/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Template](https://img.shields.io/badge/repo-template-blue)

This repository is a template for a course-specific tool that allows students to
restore write access to their GitHub Classroom repositories. Use this template
to create a new repository for each course.

The app:

- restores write access to existing repositories
- requires a GitHub App installed on the course organization
- assumes repositories follow this naming convention:

```text
{assignment_slug}-{github_username}
```

## Who This Is For

This is for instructors using GitHub Classroom who:

- manage assignments in a GitHub organization
- want a self-service way for students to regain repository access
- are comfortable running simple scripts and deploying a small web app

## Why This Tool Exists

GitHub Classroom invitations can expire, fail, or leave students without write
access. This tool provides a simple instructor-controlled way for approved
students to restore access without requiring manual reinvites.

## Prerequisites

- GitHub Classroom organization
- instructor/admin access to that organization
- GitHub account with permission to create/install GitHub Apps
- Python 3.10+
- course roster with GitHub usernames

## Quick Start

Copy runtime files:

```bash
cp .env.example .env
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp data/classroom_roster.example.csv data/classroom_roster.csv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Sync assignments and import the roster:

```bash
python scripts/sync_classroom.py
python scripts/import_whitelist.py
```

Optionally sync accepted repository data for instructor validation:

```bash
python scripts/sync_classroom.py --include-accepted
```

Run locally:

```bash
python run.py
```

Open:

```text
http://localhost:8000
```

## Typical Instructor Workflow

1. Create a course repo from this template.
2. Create and install GitHub App.
3. Configure environment variables.
4. Sync assignments.
5. Import roster.
6. Validate repositories.
7. Test with one student.
8. Deploy.
9. Share URL with students.

## How It Works

- Runtime app reads local JSON files.
- Student submits username and assignment.
- App validates whitelist and assignment.
- App grants `push` access to:

```text
{assignment_slug}-{github_username}
```

GitHub Classroom API is only used by instructor scripts, not during student
requests.

`data/accepted_assignments.json`, when generated, is an instructor validation
aid only. It is not required at runtime, and student requests still target:

```text
{assignment_slug}-{github_username}
```

## Repository Naming Requirement

> Repos must match:
>
> ```text
> {assignment_slug}-{github_username}
> ```
>
> Example:
>
> ```text
> hw-01-gchism94
> ```

If the naming pattern does not match, the app will not find the repository.

## Adding Course Data

This template does not include real course data. Real course files should be
generated or copied locally.

Assignments:

```bash
python scripts/sync_classroom.py
python scripts/sync_classroom.py --include-accepted
```

Roster:

```bash
python scripts/import_whitelist.py
```

Expected roster CSV columns:

```text
identifier,github_username,github_id,name
```

Do not commit generated course files:

- `data/classroom_roster.csv`
- `data/assignments.json`
- `data/accepted_assignments.json`
- `data/whitelist.json`

Use `data/accepted_assignments.example.json` as the safe tracked example for
accepted repository validation data.

## Instructor Scripts

- `scripts/list_classrooms.py`: list Classroom IDs available to the token
- `scripts/sync_classroom.py`: sync assignment metadata
- `scripts/import_whitelist.py`: build whitelist from roster CSV
- `scripts/validate_repos.py`: check expected repos exist
- `scripts/batch_reinvite.py`: batch restore write access for one assignment
- `scripts/view_logs.py`: read audit log entries

Common examples:

```bash
python scripts/sync_classroom.py --include-accepted
python scripts/validate_repos.py --assignment example-assignment
```

## Deployment On Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables in the Render dashboard.

## Troubleshooting

| Issue | What to check |
| --- | --- |
| Missing env vars | Copy `.env.example` and fill in required values. |
| GitHub App authentication failed | Check app ID, installation ID, org, and private key. |
| `403` permission issue | Confirm the app has repository Administration permission. |
| `404` repo not found | Check repo naming, repo existence, and app installation. |
| Username not authorized | Regenerate or edit `data/whitelist.json`. |
| Assignment not listed | Sync assignments or check `data/assignments.json`. |
| Private key path issue | Confirm `GITHUB_PRIVATE_KEY_PATH` points to the `.pem` file. |

## Safety Notes

Do not commit:

- `.env`
- `*.pem`
- `data/classroom_roster.csv`
- `data/assignments.json`
- `data/accepted_assignments.json`
- `data/whitelist.json`
- `logs/`
- `reports/`

Only commit example files.

## Design Principles

- Minimal dependencies
- No database required
- Instructor-controlled configuration
- No runtime dependency on GitHub Classroom API
- Safe handling of student data

## Project Structure

- `app/`: FastAPI app, validation, GitHub clients, audit logging
- `scripts/`: instructor utilities
- `data/`: example data files and ignored runtime data
- `docs/`: instructor and student documentation
- `tests/`: pytest test suite

## Full Documentation

- [Instructor setup](docs/instructor_setup.md)
- [Student instructions](docs/student_instructions.md)
- [Template checklist](TEMPLATE_CHECKLIST.md)
