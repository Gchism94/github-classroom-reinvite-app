from app.github_app import create_jwt, get_installation_token


def create_app_jwt() -> str:
    return create_jwt()


def get_installation_access_token() -> str:
    return get_installation_token()
