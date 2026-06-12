import os
from urllib.parse import parse_qs, urlparse

from __init__ import create_app


def _build_test_app():
    os.environ["CLIENT_SECRET"] = "test-secret"
    app = create_app()
    app.config.update(
        TESTING=True,
        CLIENT_SECRET="test-secret",
        CLIENT_ID="test-client-id",
        AUTHORIZATION_URL="https://github.com/login/oauth/authorize",
        TOKEN_URL="https://github.com/login/oauth/access_token",
        SCOPE="read:user user:email",
        CALLBACK_URL="https://example.test/oauth/callback",
        CALLBACK_URL_DEV=None,
        CALLBACK_URL_PROD=None,
    )
    return app


def test_fetch_github_metadata_redirects_with_expected_callback():
    app = _build_test_app()

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata")

    assert response.status_code == 302
    location = response.headers["Location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)

    assert parsed.netloc == "github.com"
    assert query["client_id"][0] == "test-client-id"
    assert query["redirect_uri"][0] == "https://example.test/oauth/callback"


def test_callback_rejects_invalid_state():
    app = _build_test_app()

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=wrong-state")

    assert response.status_code == 400
    assert b"Invalid state parameter" in response.data


def test_fetch_github_metadata_returns_500_when_oauth_is_incomplete(monkeypatch):
    monkeypatch.setenv("CLIENT_ID", "")
    app = _build_test_app()
    app.config["CLIENT_ID"] = None

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata")

    assert response.status_code == 500
    assert b"OAuth configuration is incomplete" in response.data
