# Instructor Setup

This guide is for instructors running the GitHub Classroom Reinvite Tool. Version
1 has no instructor login and no admin dashboard; instructor operations happen
through scripts and environment variables.

## Using This Template For A New Course

1. Create a new repository from this template.
2. Clone the new course-specific repository.
3. Copy example runtime files:

```bash
cp data/assignments.example.json data/assignments.json
cp data/whitelist.example.json data/whitelist.json
cp .env.example .env
```

4. Add `.env` values for the course.
5. Add the GitHub App private key locally, or configure it as a deployment
   secret in your hosting provider.
6. Sync assignments:

```bash
python scripts/sync_classroom.py
```

7. Import the GitHub Classroom roster:

```bash
python scripts/import_whitelist.py classroom_roster.csv
```

8. Validate expected repositories:

```bash
python scripts/validate_repos.py --assignment example-assignment
```

9. Deploy the app.

Generated files such as `data/assignments.json`, `data/whitelist.json`,
`data/accepted_assignments.json`, `logs/`, and `reports/` are ignored by git.

## Create the GitHub App

1. Go to GitHub organization settings for the organization that owns the
   Classroom repositories.
2. Open **Developer settings** and create a new GitHub App.
3. Set a clear name, such as `Classroom Reinvite Tool`.
4. Set the homepage URL to your deployed app URL, or a placeholder while testing.
5. Disable webhook delivery if you do not need webhooks for this app.
6. Generate a private key and keep it out of git.
7. Note the app ID.

## Required Permissions

For restoring write access to student repositories, start with these repository
permissions:

- Administration: Read and write
- Metadata: Read-only

The app must be able to call:

```text
PUT /repos/{owner}/{repo}/collaborators/{username}
```

Install the app only on the organization or repositories it needs.

## Install the App

Install the GitHub App on the organization that owns the GitHub Classroom
repositories. After installation, note the installation ID. You can find it in
the installation URL, or through GitHub's app installation API.

## Configure `.env`

Create a local `.env` file:

```bash
cp .env.example .env
```

Required for the web app:

```bash
GITHUB_APP_ID=123456
GITHUB_INSTALLATION_ID=987654
GITHUB_ORG=your-classroom-org
GITHUB_PRIVATE_KEY_PATH=./private-key.pem
COURSE_NAME="Example Course"
```

Optional for Classroom sync:

```bash
GITHUB_CLASSROOM_ID=123456
GITHUB_CLASSROOM_TOKEN=github_pat_or_app_user_token
```

Do not store secrets in JSON files. Do not commit `.env`, private keys, or
tokens.

## Sync Assignments

GitHub Classroom assignment sync is run from a script:

First list classrooms to find the ID:

```bash
python scripts/list_classrooms.py
```

Set `GITHUB_CLASSROOM_ID` in `.env`, then run:

```bash
python scripts/sync_classroom.py
```

The script reads `GITHUB_CLASSROOM_ID` from `.env` and writes assignment metadata
to:

```text
data/assignments.json
```

Each imported assignment includes:

- `id`
- `title`
- `slug`
- `invite_link`
- `type`
- `deadline`
- `accepted`
- `submitted`
- `passing`

The app uses `slug` as the repository prefix, so a student repo is constructed
as:

```text
{assignment.slug}-{github_username}
```

The sync script also supports:

```bash
python scripts/sync_classroom.py --classroom-id 123456
python scripts/sync_classroom.py --dry-run
python scripts/sync_classroom.py --include-accepted
```

Use `--include-accepted` to also call
`GET /assignments/{assignment_id}/accepted_assignments` for each assignment and
write `data/accepted_assignments.json`.

GitHub's Classroom REST endpoints are user-context endpoints. Set
`GITHUB_CLASSROOM_TOKEN` to a token for a classroom admin. The scripts never
print the token.

## Instructor Workflow

Use this script-only workflow for v1.

A. Sync assignments:

```bash
python scripts/sync_classroom.py
```

B. Import roster:

```bash
python scripts/import_whitelist.py classroom_roster.csv
```

C. Validate repos:

```bash
python scripts/validate_repos.py --assignment hw-01
```

D. Batch reinvite small test:

```bash
python scripts/batch_reinvite.py --assignment hw-01 --limit 2 --dry-run
```

E. Batch reinvite:

```bash
python scripts/batch_reinvite.py --assignment hw-01 --skip-missing
```

`batch_reinvite.py` requires `--assignment` so it cannot accidentally process
all assignments. Use `--limit` for small tests and `--dry-run` to preview
without changing GitHub.

## View Audit Logs

Student reinvite requests append safe JSON lines to:

```text
logs/audit.log
```

Each entry includes timestamp, username, assignment, repo, status, GitHub HTTP
status, and a safe message. Tokens, private keys, and raw GitHub API responses
are not logged.

Read recent entries with:

```bash
python scripts/view_logs.py
python scripts/view_logs.py --limit 100
python scripts/view_logs.py --json
```

## Import Or Update The Whitelist

Keep approved student usernames in:

```text
data/whitelist.json
```

Import from a CSV:

```bash
python scripts/import_whitelist.py classroom_roster.csv
```

The importer lowercases usernames, validates GitHub username format, removes
duplicates, and writes `data/whitelist.json`. Invalid usernames are skipped.

GitHub Classroom assignment sync does not import the full roster. Keep whitelist
management separate.

## Run Locally

```bash
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

## Deploy On Render

1. Create a new Render web service from this repository.
2. Set the build command:

```bash
pip install -r requirements.txt
```

3. Set the start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Add the required environment variables in Render's dashboard.
5. Add `GITHUB_CLASSROOM_TOKEN` only if you plan to run sync commands in that
   environment.

## Test With One Student Repo

1. Pick one assignment from `data/assignments.json`.
2. Confirm the assignment `slug` matches the Classroom repository prefix.
3. Add one test GitHub username to `data/whitelist.json`.
4. Confirm the expected repository exists:

```text
{assignment.slug}-{github_username}
```

5. Start the app and submit that username and assignment.
6. A `201` response from GitHub means an invitation was created.
7. A `204` response means the collaborator already has access or access was
   updated.

If the request fails, confirm the app is installed on the correct organization
and has repository administration permission.
