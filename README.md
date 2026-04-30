# GitHub Classroom Reinvite Tool

A small FastAPI app that lets approved students restore write access to GitHub
Classroom repositories. Version 1 uses whitelist validation only; it does not
include instructor login, student login, or an admin dashboard.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

Student repositories are constructed as:

```text
{assignment.slug}-{github_username}
```

## Instructor Scripts

```bash
python scripts/sync_classroom.py
python scripts/sync_classroom.py --dry-run
python scripts/import_whitelist.py students.csv
python scripts/view_logs.py
```

Assignments live in `data/assignments.json`. Approved GitHub usernames live in
`data/whitelist.json`. Do not put secrets in JSON files.

## Deployment

For Render or similar services:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure environment variables from `.env.example` in the hosting dashboard.
Never expose GitHub tokens or private keys in the browser or logs.

## Documentation

- [Instructor setup](docs/instructor_setup.md)
- [Student instructions](docs/student_instructions.md)

## Testing

```bash
pytest
```
