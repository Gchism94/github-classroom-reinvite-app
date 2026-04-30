from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.assignments import build_repo_name, load_assignments
from app.auth import is_authorized
from app.config import BASE_DIR, ConfigurationError
from app.github_app import GitHubAppAuthError
from app.github_client import GitHubClientError, add_collaborator
from app.schemas import AssignmentListResponse, ReinviteRequest, ReinviteResponse
from app.validation import is_valid_github_username, normalize_username

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def reinvite_user(
    username: str,
    assignment: str,
    add_collaborator_func=add_collaborator,
) -> ReinviteResponse:
    username = normalize_username(username)

    if not is_valid_github_username(username):
        raise HTTPException(status_code=400, detail="Invalid GitHub username.")

    if not is_authorized(username):
        raise HTTPException(
            status_code=403,
            detail="This GitHub username is not on the approved access list.",
        )

    if assignment not in load_assignments():
        raise HTTPException(status_code=400, detail="Invalid assignment.")

    repo_name = build_repo_name(assignment, username)

    try:
        status = add_collaborator_func(repo_name, username)
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: {exc}",
        ) from exc
    except GitHubAppAuthError as exc:
        raise HTTPException(
            status_code=502,
            detail="GitHub App authentication failed. Please contact your instructor.",
        ) from exc
    except GitHubClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return ReinviteResponse(repo=repo_name, status=status)


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "assignments": load_assignments()},
    )


@router.post("/", response_class=HTMLResponse)
def submit_reinvite(
    request: Request,
    username: str = Form(...),
    assignment: str = Form(...),
):
    context = {
        "request": request,
        "assignments": load_assignments(),
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
