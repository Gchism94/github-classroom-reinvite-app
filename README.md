# GitHub Classroom Reinvite App

This template creates a lightweight FastAPI web app that restores student write
access to existing GitHub Classroom repositories. It requires a GitHub App
installed on the course organization and expects repositories to be named
`assignment_slug-github_username`.

## Quick Start (10 Minutes)

1. Create a repo from this template.

2. Create and install a GitHub App.

   See [Setting Up the GitHub App](docs/instructor_setup.md#setting-up-the-github-app).

3. Copy config files:

   ```bash
   cp .env.example .env
   cp data/assignments.example.json data/assignments.json
   cp data/whitelist.example.json data/whitelist.json
   cp data/classroom_roster.example.csv data/classroom_roster.csv
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run app:

   ```bash
   python run.py
   ```

6. Open:

   ```text
   http://localhost:8000
   ```

7. Test with one student.

## How It Works

- Student enters their GitHub username.
- Student selects an assignment.
- The app checks `data/whitelist.json`.
- The app grants write access to:

```text
{assignment_slug}-{github_username}
```

## Requirements

- GitHub Classroom organization
- GitHub App installed on that organization
- Repository names following the required convention
- Assignments loaded in `data/assignments.json`
- Approved usernames loaded in `data/whitelist.json`

## Instructor Workflow

Sync assignments:

```bash
python scripts/sync_classroom.py
```

Import roster:

```bash
python scripts/import_whitelist.py
```

The shorthand above reads `data/classroom_roster.csv` by default. You can also
pass a custom path:

```bash
python scripts/import_whitelist.py data/classroom_roster.csv
```

Validate repos:

```bash
python scripts/validate_repos.py --assignment <slug>
```

## Adding Course Data

This template does not include real course data. For each course-specific repo,
instructors should generate or copy local data files from the examples.

```bash
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp data/classroom_roster.example.csv data/classroom_roster.csv
```

- `assignments.json` contains assignment metadata used by the dropdown.
- `whitelist.json` contains approved GitHub usernames.
- `data/classroom_roster.csv` is an instructor-provided GitHub Classroom roster export.
- `data/classroom_roster.csv` should not be committed.

Do not commit:

- `data/classroom_roster.csv`
- `data/assignments.json`
- `data/whitelist.json`
- `.env`
- private keys
- `logs/`
- `reports/`

Only commit:

- `data/classroom_roster.example.csv`
- `data/assignments.example.json`
- `data/whitelist.example.json`

## Repository Naming Requirement (IMPORTANT)

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

## Walkthrough: Setting Up a New Course

### 1. Create Repo From Template

What to do: create a new course-specific repository from this template.

Command:

```bash
git clone <your-course-repo-url>
cd <your-course-repo>
```

Expected outcome: you have a separate repo for the course.

### 2. Create GitHub App

What to do: create a GitHub App for the course organization.

Command: none.

Expected outcome: you have a GitHub App ID and a downloaded private key.

### 3. Install App On Course Org

What to do: install the app on the organization that owns the Classroom repos.

Command: none.

Expected outcome: you have a `GITHUB_INSTALLATION_ID`.

### 4. Set `.env` Variables

What to do: copy example files and fill in `.env`.

Command:

```bash
cp .env.example .env
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
```

Expected outcome: local runtime files exist and are ignored by git.

### 5. Sync Assignments

What to do: fetch assignment metadata from GitHub Classroom.

Command:

```bash
python scripts/sync_classroom.py
```

Expected outcome: `data/assignments.json` contains course assignments.

### 6. Import Roster

What to do: import approved GitHub usernames from the Classroom roster CSV.

Command:

```bash
python scripts/import_whitelist.py
```

Expected outcome: `data/whitelist.json` contains approved usernames.

### 7. Validate Repos

What to do: confirm expected student repos exist.

Command:

```bash
python scripts/validate_repos.py --assignment <slug>
```

Expected outcome: `reports/repo_validation_report.json` is created.

### 8. Test One Student

What to do: run a small dry run before changing access.

Command:

```bash
python scripts/batch_reinvite.py --assignment <slug> --limit 1 --dry-run
```

Expected outcome: the script prints the planned action without calling GitHub.

### 9. Deploy

What to do: deploy the app and set environment variables.

Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Expected outcome: the app is reachable at your deployment URL.

### 10. Share URL

What to do: send the deployed URL to approved students.

Command: none.

Expected outcome: students can request access from the web form.

## Troubleshooting

- `403`: permission issue; check GitHub App repository permissions.
- `404`: repo not found, naming mismatch, or app not installed on repo.
- Username not authorized: update `data/whitelist.json`.
- GitHub App auth failed: check env vars and private key path.
- Assignment not listed: sync assignments or check `data/assignments.json`.

## Deployment (Render)

Build:

```bash
pip install -r requirements.txt
```

Start:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables in the Render dashboard.

## Safety Notes

Do not commit:

- `.env`
- `*.pem`
- `data/classroom_roster.csv`
- `logs/`
- `reports/`

## Full Docs

- [Instructor setup](docs/instructor_setup.md)
- [Student instructions](docs/student_instructions.md)
