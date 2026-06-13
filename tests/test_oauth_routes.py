from urllib.parse import parse_qs, urlparse

import main as main_module
import __init__ as app_init
from __init__ import create_app


def _build_test_app(monkeypatch, tmp_path):
    secret_file = tmp_path / "client_secret.txt"
    secret_file.write_text("test-secret", encoding="utf-8")
    monkeypatch.setenv("CLIENT_SECRET_FILE", str(secret_file))
    monkeypatch.delenv("CLIENT_SECRET", raising=False)
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


def _build_test_app_without_scope(monkeypatch, tmp_path):
    monkeypatch.setattr(app_init, "SCOPE", None)
    monkeypatch.delenv("SCOPE", raising=False)
    app = _build_test_app(monkeypatch, tmp_path)
    app.config["SCOPE"] = None
    return app


def test_fetch_github_metadata_redirects_with_expected_callback(monkeypatch, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata", base_url="https://example.test")

    assert response.status_code == 302
    location = response.headers["Location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)

    assert parsed.netloc == "github.com"
    assert query["client_id"][0] == "test-client-id"
    assert query["redirect_uri"][0] == "https://example.test/oauth/callback"
    assert query["scope"][0] == "read:user user:email"


def test_fetch_github_metadata_omits_scope_when_unset(monkeypatch, tmp_path):
    app = _build_test_app_without_scope(monkeypatch, tmp_path)

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata", base_url="https://example.test")

    assert response.status_code == 302
    location = response.headers["Location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)

    assert parsed.netloc == "github.com"
    assert query["client_id"][0] == "test-client-id"
    assert query["redirect_uri"][0] == "https://example.test/oauth/callback"
    assert "scope" not in query


def test_callback_rejects_missing_code(monkeypatch, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Missing OAuth authorization code"


def test_callback_hides_non_2xx_token_endpoint_body(monkeypatch, caplog, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 400
        text = "<script>alert('xss')</script>"
        is_error = True

        def json(self):
            raise AssertionError("json() should not be called when token endpoint is non-2xx")

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return FakeTokenResponse()

        async def get(self, *args, **kwargs):
            raise AssertionError("GitHub user lookup should not be reached when token exchange fails")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.message == "Token endpoint returned an error" for record in caplog.records)
    assert any(getattr(record, "response_text", "") == "<script>alert('xss')</script>" for record in caplog.records)


def test_callback_hides_missing_access_token_details(monkeypatch, caplog, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 200
        text = "{\"error\": \"invalid_grant\", \"error_description\": \"<script>alert(1)</script>\"}"
        is_error = False

        def json(self):
            return {
                "error": "invalid_grant",
                "error_description": "<script>alert(1)</script>",
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return FakeTokenResponse()

        async def get(self, *args, **kwargs):
            raise AssertionError("GitHub user lookup should not be reached when access token is missing")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.message == "Access token missing from token response" for record in caplog.records)
    assert any(getattr(record, "error_description", "") == "<script>alert(1)</script>" for record in caplog.records)


def test_callback_rejects_invalid_state(monkeypatch, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=wrong-state")

    assert response.status_code == 400
    assert b"Invalid state parameter" in response.data


def test_callback_rejects_missing_state(monkeypatch, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        response = client.get("/oauth/callback?code=abc123")

    assert response.status_code == 400
    assert b"Invalid state parameter" in response.data


def test_callback_hides_provider_error_details(monkeypatch, caplog, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    with app.test_client() as client:
        response = client.get(
            "/oauth/callback?error=access_denied&error_description=<script>alert(1)</script>",
        )

    assert response.status_code == 400
    assert response.data == b"OAuth authorization failed"
    assert b"script" not in response.data
    assert any(record.message == "OAuth callback returned error from provider" for record in caplog.records)
    assert any(getattr(record, "oauth_error_description", "") == "<script>alert(1)</script>" for record in caplog.records)


def test_callback_hides_token_endpoint_body(monkeypatch, caplog, tmp_path):
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 400
        text = "<script>alert('xss')</script>"
        is_error = True

        def json(self):
            return {"error": "invalid_grant", "error_description": "<script>alert(1)</script>"}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return FakeTokenResponse()

        async def get(self, *args, **kwargs):
            raise AssertionError("GitHub user lookup should not be reached when token exchange fails")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.message == "Token endpoint returned an error" for record in caplog.records)


def test_fetch_github_metadata_returns_500_when_oauth_is_incomplete(monkeypatch, tmp_path):
    monkeypatch.setenv("CLIENT_ID", "")
    app = _build_test_app(monkeypatch, tmp_path)
    app.config["CLIENT_ID"] = None

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata")

    assert response.status_code == 500
    assert b"OAuth configuration is incomplete" in response.data
