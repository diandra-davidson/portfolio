import json
import sys
from pathlib import Path
from types import TracebackType
from urllib.parse import parse_qs, urlparse
from typing import Any
from flask import Flask

TEST_AWS_SECRET_ID = "test/portfolio/github-oauth"
TEST_AWS_REGION = "us-east-1"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import main as main_module
import pytest
import __init__ as app_init
from __init__ import create_app


def _mock_aws_secret(
    monkeypatch: pytest.MonkeyPatch,
    secret_value: str,
    expected_secret_id: str,
    expected_region: str,
) -> None:
    class FakeSecretsManagerClient:
        def get_secret_value(self, *, SecretId: str) -> dict[str, str]:
            assert SecretId == expected_secret_id
            payload = {"client_secret": secret_value}
            return {"SecretString": json.dumps(payload)}

    def fake_boto3_client(service_name: str, region_name: str | None = None) -> FakeSecretsManagerClient:
        assert service_name == "secretsmanager"
        assert region_name == expected_region
        return FakeSecretsManagerClient()

    monkeypatch.setitem(sys.modules, "boto3", type("FakeBoto3", (), {"client": staticmethod(fake_boto3_client)}))


def _build_test_app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Flask:
    _ = tmp_path
    _mock_aws_secret(
        monkeypatch,
        "test-secret",
        expected_secret_id=TEST_AWS_SECRET_ID,
        expected_region=TEST_AWS_REGION,
    )

    monkeypatch.setenv("AWS_SECRETSMANAGER_SECRET_NAME", TEST_AWS_SECRET_ID)
    monkeypatch.setenv("AWS_SECRETSMANAGER_SERVICE_NAME", "client_secret")
    monkeypatch.setenv("AWS_REGION", TEST_AWS_REGION)
    monkeypatch.delenv("AWS_SECRETSMANAGER_FLASK_SECRET_NAME", raising=False)
    monkeypatch.delenv("AWS_SECRETSMANAGER_FLASK_SERVICE_NAME", raising=False)
    monkeypatch.delenv("AWS_SECRETSMANAGER_FLASK_REGION", raising=False)

    # __init__.py reads these values at import time, so patch module constants too.
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_SECRET_NAME", TEST_AWS_SECRET_ID)
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_SERVICE_NAME", "client_secret")
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_REGION", TEST_AWS_REGION)
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_FLASK_SECRET_NAME", None)
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_FLASK_SERVICE_NAME", None)
    monkeypatch.setattr(app_init, "AWS_SECRETSMANAGER_FLASK_REGION", None)

    monkeypatch.delenv("CALLBACK_URL", raising=False)
    monkeypatch.delenv("CALLBACK_URL_DEV", raising=False)
    monkeypatch.delenv("CALLBACK_URL_PROD", raising=False)
    monkeypatch.delenv("CLIENT_SECRET", raising=False)
    monkeypatch.delenv("CLIENT_SECRET_FILE", raising=False)

    app: Flask = create_app()

    app.config["TESTING"] = True
    app.config["CLIENT_SECRET"] = "test-secret"
    app.config["CLIENT_ID"] = "test-client-id"
    app.config["AUTHORIZATION_URL"] = "https://github.com/login/oauth/authorize"
    app.config["TOKEN_URL"] = "https://github.com/login/oauth/access_token"
    app.config["SCOPE"] = "read:user user:email"
    app.config["CALLBACK_URL"] = "https://example.test/oauth/callback"
    app.config["CALLBACK_URL_DEV"] = None
    app.config["CALLBACK_URL_PROD"] = None
    return app


def _build_test_app_without_scope(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Flask:
    monkeypatch.setattr(app_init, "SCOPE", None)
    monkeypatch.delenv("SCOPE", raising=False)
    app = _build_test_app(monkeypatch, tmp_path)
    app.config["SCOPE"] = None
    return app


def test_fetch_github_metadata_redirects_with_expected_callback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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


def test_fetch_github_metadata_omits_scope_when_unset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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


def test_callback_rejects_missing_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Missing OAuth authorization code"


def test_callback_hides_non_2xx_token_endpoint_body(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 400
        text = "<script>alert('xss')</script>"
        is_error = True
        headers = {"content-type": "text/plain"}

        def json(self) -> Any:
            raise AssertionError("json() should not be called when token endpoint is non-2xx")

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> FakeTokenResponse:
            return FakeTokenResponse()

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            raise AssertionError("GitHub user lookup should not be reached when token exchange fails")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.getMessage() == "Token endpoint returned an error" for record in caplog.records)
    assert any(getattr(record, "response_hash", "") for record in caplog.records)
    assert any(getattr(record, "response_length", 0) > 0 for record in caplog.records)


def test_callback_hides_missing_access_token_details(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 200
        text = "{\"error\": \"invalid_grant\", \"error_description\": \"<script>alert(1)</script>\"}"
        is_error = False

        def json(self) -> dict[str, str]:
            return {
                "error": "invalid_grant",
                "error_description": "<script>alert(1)</script>",
            }

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> FakeTokenResponse:
            return FakeTokenResponse()

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            raise AssertionError("GitHub user lookup should not be reached when access token is missing")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.getMessage() == "Access token missing from token response" for record in caplog.records)
    assert any(getattr(record, "error_description", "") == "<script>alert(1)</script>" for record in caplog.records)


def test_callback_rejects_invalid_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=wrong-state")

    assert response.status_code == 400
    assert b"Invalid state parameter" in response.data


def test_callback_rejects_missing_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    with app.test_client() as client:
        response = client.get("/oauth/callback?code=abc123")

    assert response.status_code == 400
    assert b"Invalid state parameter" in response.data


def test_callback_hides_provider_error_details(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get(
            "/oauth/callback?error=access_denied&error_description=<script>alert(1)</script>&state=expected-state",
        )

    assert response.status_code == 400
    assert response.data == b"OAuth authorization failed"
    assert b"script" not in response.data
    assert any(record.getMessage() == "OAuth callback returned error from provider" for record in caplog.records)
    assert any(getattr(record, "oauth_error_description", "") == "<script>alert(1)</script>" for record in caplog.records)


def test_callback_hides_token_endpoint_body(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    caplog.set_level("WARNING", logger="main")

    class FakeTokenResponse:
        status_code = 400
        text = "<script>alert('xss')</script>"
        is_error = True
        headers = {"content-type": "text/plain"}

        def json(self) -> dict[str, str]:
            return {"error": "invalid_grant", "error_description": "<script>alert(1)</script>"}

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> FakeTokenResponse:
            return FakeTokenResponse()

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            raise AssertionError("GitHub user lookup should not be reached when token exchange fails")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 400
    assert response.data == b"Token exchange failed"
    assert b"script" not in response.data
    assert any(record.getMessage() == "Token endpoint returned an error" for record in caplog.records)


def test_callback_returns_500_when_client_secret_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)
    app.config["CLIENT_SECRET"] = None

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 500
    assert response.data == b"OAuth configuration is incomplete on the server"


def test_callback_returns_502_when_token_request_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> Any:
            request = main_module.httpx.Request("POST", "https://github.com/login/oauth/access_token")
            raise main_module.httpx.RequestError("network failure", request=request)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            raise AssertionError("GitHub user lookup should not be reached when token request fails")

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 502
    assert response.data == b"OAuth upstream request failed"


def test_callback_returns_502_when_github_metadata_json_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    app = _build_test_app(monkeypatch, tmp_path)

    class FakeTokenResponse:
        status_code = 200
        is_error = False
        text = '{"access_token":"abc123"}'

        def json(self) -> dict[str, str]:
            return {"access_token": "abc123"}

    class FakeGithubResponse:
        status_code = 200
        text = "not-json"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> Any:
            raise ValueError("invalid json")

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> FakeTokenResponse:
            return FakeTokenResponse()

        async def get(self, *args: Any, **kwargs: Any) -> FakeGithubResponse:
            return FakeGithubResponse()

    monkeypatch.setattr(main_module.httpx, "AsyncClient", FakeAsyncClient)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_state"] = "expected-state"

        response = client.get("/oauth/callback?code=abc123&state=expected-state")

    assert response.status_code == 502
    assert response.data == b"Failed to fetch GitHub metadata"


def test_fetch_github_metadata_returns_500_when_oauth_is_incomplete(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("CLIENT_ID", "")
    app = _build_test_app(monkeypatch, tmp_path)
    app.config["CLIENT_ID"] = None

    with app.test_client() as client:
        response = client.get("/fetch/github_metadata")

    assert response.status_code == 500
    assert b"OAuth configuration is incomplete" in response.data
