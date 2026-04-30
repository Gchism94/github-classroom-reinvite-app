from types import SimpleNamespace

from app.github_client import add_collaborator


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_add_collaborator_uses_push_permission_and_installation_token(monkeypatch):
    settings = SimpleNamespace(
        github_org="course-org",
        validate_github_app_config=lambda: None,
    )
    calls = {}

    def fake_put(url, headers, json, timeout):
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json
        calls["timeout"] = timeout
        return FakeResponse(201)

    monkeypatch.setattr("app.github_client.get_settings", lambda: settings)
    monkeypatch.setattr("app.github_client.get_installation_token", lambda settings: "token")
    monkeypatch.setattr("app.github_client.requests.put", fake_put)

    result = add_collaborator("hw-01-octocat", "octocat")

    assert calls["url"] == (
        "https://api.github.com/repos/course-org/"
        "hw-01-octocat/collaborators/octocat"
    )
    assert calls["headers"]["Authorization"] == "Bearer token"
    assert calls["headers"]["Accept"] == "application/vnd.github+json"
    assert calls["json"] == {"permission": "push"}
    assert calls["timeout"] == 20
    assert result.github_http_status == 201
    assert result.message == "Invitation created. Check your GitHub notifications or email."
