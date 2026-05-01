# Instructor Setup

This app is a reusable GitHub Classroom Reinvite App template. Version 1 has no
instructor login and no admin dashboard. Instructor tasks happen through scripts.

## Template Purpose

Use this repository as a template, then create one course-specific repository per
course or offering. Course-specific data should not be committed to the template
repo.

Do not commit:

- `.env`
- private keys
- `data/classroom_roster.csv`
- logs or reports
- real `data/assignments.json`
- real `data/whitelist.json`

Only commit:

- `data/classroom_roster.example.csv`
- `data/assignments.example.json`
- `data/whitelist.example.json`

## What The App Does

Students enter their GitHub username, select an assignment, and request access.
The app checks the local whitelist and restores write access to the expected
existing repository:

```text
{assignment_slug}-{github_username}
```

## What The App Does Not Do

- It does not create repositories.
- It does not enroll students in a classroom.
- It does not replace GitHub Classroom.
- It only restores collaborator/write access for existing repos.

## Quick Workflow

1. Create a repo from this template.
2. Create/install a GitHub App in the course organization.
3. Copy example config files.
4. Fill in `.env`.
5. Sync assignments.
6. Import roster.
7. Validate repos.
8. Test one student.
9. Deploy.
10. Share URL with students.

## First Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp data/classroom_roster.example.csv data/classroom_roster.csv
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

## Setting Up the GitHub App

### 1. Create The GitHub App

Go to:

```text
GitHub -> Settings -> Developer settings -> GitHub Apps -> New GitHub App
```

Set:

- App name: `<course-name>-reinvite-app`
- Homepage URL: `http://localhost:8000` for local testing, or your deployment
  URL later
- Webhook: disable

### 2. Set Permissions

Under **Repository permissions**, set:

- Administration: Read and write
- Metadata: Read-only

These permissions are required so the app can add collaborators to repositories.

### 3. Install The App

1. Click **Install App**.
2. Select the course organization, meaning the organization that owns the
   GitHub Classroom repositories.
3. Choose **All repositories**. This is recommended for Classroom courses
   because student repositories are often created over time.

The app must be installed on the organization that owns the GitHub Classroom
repositories.

### 4. Get Required Values

`GITHUB_APP_ID`:

- Found on the GitHub App settings page.

`GITHUB_INSTALLATION_ID`:

- Go to `https://github.com/settings/installations`.
- Click the app.
- Copy the number from the URL:

```text
https://github.com/settings/installations/<INSTALLATION_ID>
```

`GITHUB_ORG`:

- The GitHub organization name.
- Example: `https://github.com/ua-datascience` -> `ua-datascience`

`GITHUB_PRIVATE_KEY`:

- On the GitHub App page, generate a private key.
- Download the `.pem` file.

### 5. Configure Environment Variables

Use a private key file path locally:

```bash
GITHUB_APP_ID=
GITHUB_INSTALLATION_ID=
GITHUB_ORG=
GITHUB_PRIVATE_KEY_PATH=./private-key.pem
COURSE_NAME="Example Course"
```

Do not commit the private key. Keep `*.pem` in `.gitignore`.

### 6. Verify Setup

Run the app and submit a test request for one whitelisted student and one known
repository.

Expected GitHub results:

- `201`: invitation created
- `204`: access already granted or updated
- `403`: permission issue
- `404`: repo not found or app not installed on repo

### 7. Common Mistakes

- App not installed on the organization
- Wrong installation ID
- Private key path incorrect
- Using `GITHUB_PRIVATE_KEY` instead of `GITHUB_PRIVATE_KEY_PATH`
- App missing Administration permission

## Classroom Sync

The student-facing app does not call the Classroom API at runtime. Classroom API
access is only used by instructor scripts.

`GITHUB_CLASSROOM_TOKEN` is only needed for instructor scripts.
`GITHUB_CLASSROOM_ID` identifies the classroom to sync.

```bash
python scripts/list_classrooms.py
python scripts/sync_classroom.py --dry-run
python scripts/sync_classroom.py
```

To also save accepted assignment data:

```bash
python scripts/sync_classroom.py --include-accepted
```

## Adding Roster and Assignment Data

### Assignment Data

Preferred method:

```bash
python scripts/sync_classroom.py
```

Manual fallback:

```bash
cp data/assignments.example.json data/assignments.json
```

Then edit `data/assignments.json` using `data/assignments.example.json` as a
guide.

Required field for app behavior:

- `slug`

### Roster / Whitelist Data

Preferred method:

1. Download/export the GitHub Classroom roster CSV.
2. Save it as `data/classroom_roster.csv`.
3. Run:

```bash
python scripts/import_whitelist.py
python scripts/import_whitelist.py data/classroom_roster.csv
```

Expected CSV columns:

```text
identifier, github_username, github_id, name
```

Only `github_username` is required for whitelist generation. Rows with missing
`github_username` are skipped. Usernames are normalized to lowercase. Invalid
GitHub usernames are skipped or reported by the script. The generated
`data/whitelist.json` is used by the student-facing app.

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

## Import Roster

Export the GitHub Classroom roster CSV, then run:

```bash
python scripts/import_whitelist.py --dry-run
python scripts/import_whitelist.py
```

The importer reads the `github_username` column, lowercases usernames, validates
them, deduplicates them, and writes `data/whitelist.json`.

## Validate Repos

Check that expected repos exist for one assignment:

```bash
python scripts/validate_repos.py --assignment hw-01
```

## Batch Reinvite

Preview a small batch:

```bash
python scripts/batch_reinvite.py --assignment hw-01 --limit 2 --dry-run
```

Run the batch:

```bash
python scripts/batch_reinvite.py --assignment hw-01 --skip-missing
```

Batch reinvite requires `--assignment`; it never batches every assignment by
default.

## Audit Logs

Inspect recent events:

```bash
python scripts/view_logs.py
python scripts/view_logs.py --limit 100
```

Audit logs include timestamp, username, assignment, repo, status, GitHub HTTP
status, and a safe message. Tokens, private keys, and raw GitHub API responses
are not logged.

## Render Deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables from `.env.example` in Render. Add the private key as
a deployment secret or environment value. Do not upload local `.env` files.

## Troubleshooting

- Missing env vars: copy `.env.example` and fill in required values.
- GitHub App authentication failed: check app ID, installation ID, org, and key.
- 403 permission issue: confirm the app has collaborator/admin permissions.
- 404 repo not found: confirm the repo exists and the app is installed on it.
- Username not authorized: update the roster and regenerate `whitelist.json`.
- Assignment not listed: sync assignments or check `assignments.json`.
- Repo slug mismatch: confirm assignment `slug` matches the repo prefix.

## Final Pre-Launch Checklist

- [ ] `pytest` passes
- [ ] `data/assignments.json` generated
- [ ] `data/whitelist.json` generated
- [ ] Test repo exists
- [ ] One test reinvite succeeds
- [ ] Audit log records event
- [ ] Deployment env vars are set
- [ ] Student URL works
