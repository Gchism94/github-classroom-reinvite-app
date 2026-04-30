from fastapi import APIRouter, HTTPException
from app.assignments import build_repo_name, is_valid_assignment, load_assignments
from app.auth import is_authorized, is_valid_github_username, normalize_username
from app.github_client import GitHubClientError, add_collaborator_with_write_access
from app.schemas import AssignmentListResponse, ReinviteRequest, ReinviteResponse

router = APIRouter()


@router.get("/api/assignments", response_model=AssignmentListResponse)
def get_assignments():
    return AssignmentListResponse(assignments=load_assignments())


@router.post("/api/reinvite", response_model=ReinviteResponse)
def reinvite(req: ReinviteRequest):
    username = normalize_username(req.username)

    if not is_valid_github_username(username):
        raise HTTPException(status_code=400, detail="Invalid GitHub username.")

    if not is_authorized(username):
        raise HTTPException(status_code=403, detail="This GitHub username is not authorized.")

    if not is_valid_assignment(req.assignment):
        raise HTTPException(status_code=400, detail="Invalid assignment.")

    repo_name = build_repo_name(req.assignment, username)

    try:
        add_collaborator_with_write_access(repo_name, username)
    except GitHubClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return ReinviteResponse(repo=repo_name, status="Invitation sent or access granted")
