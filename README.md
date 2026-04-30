# GitHub Classroom Reinvite Tool

A lightweight FastAPI web app that lets approved students restore write access
to GitHub Classroom repositories using a GitHub App installation token.

## Why GitHub App instead of a PAT?

A GitHub App is safer and more publishable than a personal access token because permissions are scoped to the app installation and can be limited to specific repositories or an organization.

## Features

- Whitelist-based student access
- Assignment dropdown / API selection
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
  "hw-01",
  "hw-02",
  "project-proposal"
]
```

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
