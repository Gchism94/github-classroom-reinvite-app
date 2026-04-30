from pydantic import BaseModel, Field


class ReinviteRequest(BaseModel):
    username: str = Field(..., description="GitHub username")
    assignment: str = Field(..., description="Assignment prefix")


class ReinviteResponse(BaseModel):
    repo: str
    status: str


class AssignmentListResponse(BaseModel):
    assignments: list[str]
