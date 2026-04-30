# GitHub Classroom Reinvite Tool

A lightweight FastAPI web app that lets approved students restore write access
to GitHub Classroom repositories using a GitHub App installation token.

## Why GitHub App instead of a PAT?

A GitHub App is safer and more publishable than a personal access token because permissions are scoped to the app installation and can be limited to specific repositories or an organization.

## Features

- Whitelist-based student access
- Assignment dropdown / API selection
- GitHub Classroom assignment sync for instructors
- GitHub App authentication using a private key
- Server-side collaborator invitation with write access
- JSON-configurable assignments and whitelist
- Basic tests and CI scaffold

## Repository naming convention

This app assumes individual GitHub Classroom repositories are named like:

```text
{assignment-prefix}-{github-username}
```

Example:

```text
hw-01-octocat
```

## Local Setup

```bash
git clone https://github.com/YOUR_ORG/github-classroom-reinvite-app.git
cd github-classroom-reinvite-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your GitHub App credentials. The private key must stay
server-side and can be pasted as a quoted value with `\n` line breaks.

Then run:

```bash
python run.py
```

Open:

```text
http://localhost:8000
```

## Environment variables

See `.env.example`.

Required:

- `GITHUB_APP_ID`
- `GITHUB_INSTALLATION_ID`
- `GITHUB_ORG`
- `GITHUB_PRIVATE_KEY`

Optional for GitHub Classroom sync:

- `GITHUB_CLASSROOM_ID`
- `GITHUB_CLASSROOM_TOKEN`

The repository collaborator reinvite flow uses a GitHub App installation token.
The GitHub Classroom REST endpoints are user-context endpoints in GitHub's
documentation and support GitHub App user access tokens or fine-grained personal
access tokens. Set `GITHUB_CLASSROOM_TOKEN` to a token for a classroom admin when
running the sync script.

## GitHub App Permissions

Create a GitHub App with the minimum permissions needed to invite collaborators to repositories.

Recommended starting point:

- Repository permissions:
  - Administration: Read and write
  - Metadata: Read-only

Install the app on the organization that owns the GitHub Classroom repositories.

## Data files

Edit these files:

```text
data/whitelist.json
data/assignments.json
```

Example `whitelist.json`:

```json
[
  "octocat",
  "student-user"
]
```

Example `assignments.json`:

```json
[
  {
    "id": 123,
    "title": "Homework 01",
    "slug": "hw-01",
    "invite_link": "https://classroom.github.com/a/example",
    "deadline": "2026-05-01T23:59:00Z"
  }
]
```

`slug` is used as the repository prefix, so the app constructs repository names
as:

```text
{assignment.slug}-{github_username}
```

`data/accepted_assignments.json` stores accepted Classroom assignment repository
metadata from the sync script. It is not used as the whitelist.

## Syncing GitHub Classroom assignments

Set `GITHUB_CLASSROOM_TOKEN` in `.env`. If you know the classroom ID, also set
`GITHUB_CLASSROOM_ID`:

```bash
GITHUB_CLASSROOM_ID=123456
GITHUB_CLASSROOM_TOKEN=github_pat_or_app_user_token
```

Then run:

```bash
python scripts/sync_classroom.py
```

The script fetches:

- `GET /classrooms`
- `GET /classrooms/{classroom_id}/assignments`
- `GET /assignments/{assignment_id}/accepted_assignments`

It writes imported assignments to `data/assignments.json` and accepted
assignment repositories to `data/accepted_assignments.json`.

If `GITHUB_CLASSROOM_ID` is not configured and the token can access exactly one
classroom, that classroom is used. If multiple classrooms are returned, the
script prints their IDs and exits; re-run it with:

```bash
python scripts/sync_classroom.py --classroom-id 123456
```

To skip accepted-assignment fetching:

```bash
python scripts/sync_classroom.py --skip-accepted
```

GitHub Classroom does not expose the full roster through these assignment sync
endpoints. Keep approved student access separate in `data/whitelist.json`.

## API usage

POST to `/api/reinvite`:

```json
{
  "username": "octocat",
  "assignment": "hw-01"
}
```

Response:

```json
{
  "repo": "hw-01-octocat",
  "status": "Invitation sent or access granted"
}
```

## Security notes

- Never commit `.env` or private keys.
- Keep the private key server-side only.
- Keep the whitelist explicit.
- This app intentionally does not implement GitHub OAuth yet; students enter
  their GitHub username and the server checks `data/whitelist.json`.
- Consider adding GitHub OAuth later so users cannot claim another whitelisted username.
- Use rate limiting before public deployment.

## Deploying

For Render or similar services, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set the four required GitHub environment variables in the service dashboard.

## Tests

```bash
pytest
```

## Roadmap ideas

- GitHub OAuth login
- Instructor dashboard
- Automatic assignment discovery
- Audit logs
- Admin upload for whitelist CSV
- Docker deployment
