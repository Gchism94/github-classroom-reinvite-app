from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.assignments import build_repo_name, load_assignment_records, load_assignments
from app.auth import is_authorized
from app.audit import append_audit_log
from app.config import BASE_DIR, ConfigurationError
from app.github_app import GitHubAppAuthError
from app.github_client import GitHubClientError, add_collaborator
from app.schemas import AssignmentListResponse, ReinviteRequest, ReinviteResponse
from app.validation import is_valid_github_username, normalize_username

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _result_message(result: Any) -> str:
    return result.message if hasattr(result, "message") else str(result)


def _result_github_status(result: Any) -> int | None:
    return getattr(result, "github_http_status", None)


def reinvite_user(
    username: str,
    assignment: str,
    add_collaborator_func=add_collaborator,
) -> ReinviteResponse:
    username = normalize_username(username)
    repo_name = None

    if not is_valid_github_username(username):
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=None,
            message="Invalid GitHub username.",
        )
        raise HTTPException(status_code=400, detail="Invalid GitHub username.")

    if not is_authorized(username):
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=None,
            message="This GitHub username is not on the approved access list.",
        )
        raise HTTPException(
            status_code=403,
            detail="This GitHub username is not on the approved access list.",
        )

    if assignment not in load_assignments():
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=None,
            message="Invalid assignment.",
        )
        raise HTTPException(status_code=400, detail="Invalid assignment.")

    repo_name = build_repo_name(assignment, username)

    try:
        collaborator_result = add_collaborator_func(repo_name, username)
        status = _result_message(collaborator_result)
        github_http_status = _result_github_status(collaborator_result)
    except ConfigurationError as exc:
        message = f"Server configuration error: {exc}"
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=None,
            message=message,
        )
        raise HTTPException(
            status_code=500,
            detail=message,
        ) from exc
    except GitHubAppAuthError as exc:
        message = "GitHub App authentication failed. Please contact your instructor."
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=None,
            message=message,
        )
        raise HTTPException(
            status_code=502,
            detail=message,
        ) from exc
    except GitHubClientError as exc:
        append_audit_log(
            username=username,
            assignment=assignment,
            repo=repo_name,
            status="failure",
            github_http_status=exc.github_http_status,
            message=exc.message,
        )
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    append_audit_log(
        username=username,
        assignment=assignment,
        repo=repo_name,
        status="success",
        github_http_status=github_http_status,
        message=status,
    )
    return ReinviteResponse(repo=repo_name, status=status)


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "assignments": load_assignment_records()},
    )


@router.post("/", response_class=HTMLResponse)
def submit_reinvite(
    request: Request,
    username: str = Form(...),
    assignment: str = Form(...),
):
    context = {
        "request": request,
        "assignments": load_assignment_records(),
        "selected_assignment": assignment,
        "username": username,
    }
    try:
        result = reinvite_user(username, assignment)
        context["success"] = result.status
        context["repo"] = result.repo
    except HTTPException as exc:
        context["error"] = exc.detail

    return templates.TemplateResponse("index.html", context)


@router.get("/api/assignments", response_model=AssignmentListResponse)
def get_assignments():
    return AssignmentListResponse(assignments=load_assignments())


@router.post("/api/reinvite", response_model=ReinviteResponse)
def reinvite(req: ReinviteRequest):
    return reinvite_user(req.username, req.assignment)
