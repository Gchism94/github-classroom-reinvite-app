# GitHub Classroom Reinvite App

A lightweight FastAPI app that lets whitelisted students restore write access to
their GitHub Classroom repositories. It uses a GitHub App installation token for
repository collaborator updates and keeps v1 instructor work in scripts, not an
admin dashboard.

Student repository names are constructed as:

```text
{assignment.slug}-{github_username}
```

## Use This As A Template

This repository is designed to be safe as a GitHub Template Repository. It
contains source code, docs, tests, scripts, and example config files only. It
does not track real assignments, rosters, logs, reports, `.env` files, or
private keys.

For each course:

1. Create a new repository from this template.
2. Clone the course-specific repository.
3. Copy the example runtime files:

```bash
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp .env.example .env
```

4. Configure `.env` for that course.
5. Sync assignments and import the course roster.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp .env.example .env
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

## GitHub App Setup

Create a GitHub App in the organization that owns the GitHub Classroom
repositories. The app needs repository permissions sufficient to add
collaborators:

- Administration: Read and write
- Metadata: Read-only

Install the app on the course organization or selected course repositories, then
set:

```bash
GITHUB_APP_ID=
GITHUB_INSTALLATION_ID=
GITHUB_ORG=
GITHUB_PRIVATE_KEY_PATH=./private-key.pem
COURSE_NAME="Example Course"
```

Keep the private key and `.env` out of git.

## Classroom Sync

GitHub Classroom sync is instructor-triggered only. Student requests never call
the Classroom API.

Find the classroom ID:

```bash
python scripts/list_classrooms.py
```

Set `GITHUB_CLASSROOM_ID` and `GITHUB_CLASSROOM_TOKEN` in `.env`, then sync:

```bash
python scripts/sync_classroom.py
python scripts/sync_classroom.py --dry-run
python scripts/sync_classroom.py --include-accepted
```

The generated `data/assignments.json` and
`data/accepted_assignments.json` files are ignored by git.

## Roster Import

Import a GitHub Classroom roster CSV with columns:

```text
identifier, github_username, github_id, name
```

```bash
python scripts/import_whitelist.py classroom_roster.csv
python scripts/import_whitelist.py classroom_roster.csv --dry-run
```

The generated `data/whitelist.json` file is ignored by git.

## Local Test

Validate expected repositories for one assignment:

```bash
python scripts/validate_repos.py --assignment example-assignment
```

Preview a batch reinvite:

```bash
python scripts/batch_reinvite.py --assignment example-assignment --limit 2 --dry-run
```

Run the app and test one whitelisted student before sharing the URL.

## Render Deployment

For Render or similar services:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables from `.env.example` in the hosting dashboard. Add the
GitHub App private key as a deployment secret or environment value supported by
your host. Do not commit private keys, tokens, generated JSON files, logs, or
reports.

## Documentation

- [Instructor setup](docs/instructor_setup.md)
- [Student instructions](docs/student_instructions.md)
- [Template checklist](TEMPLATE_CHECKLIST.md)

## Testing

```bash
pytest
```
