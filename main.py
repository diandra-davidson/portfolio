"""
Main entry point for the Python application.
"""
import logging
import os
import secrets
import httpx
from typing import Any, cast
from urllib.parse import urlparse
from flask import request, render_template, Blueprint, redirect, session, url_for, current_app
from flask.typing import ResponseReturnValue


bp = Blueprint("main", __name__)
OAUTH_CALLBACK_PATH = '/oauth/callback'
LOGGER = logging.getLogger(__name__)


def _cfg(key: str) -> str | None:
    """Return OAuth-related config value from app config, then environment."""
    config = cast(dict[str, Any], current_app.config)
    config_value = config.get(key)
    if isinstance(config_value, str) and config_value:
        return config_value
    return os.getenv(key)


def _normalized_host(value: str | None) -> str | None:
    """Return normalized host without userinfo/port, or None when unavailable."""
    if not value:
        return None
    parsed = urlparse(f"//{value}")
    host = parsed.hostname.lower() if parsed.hostname else None
    return host or None


def _url_host(value: str | None) -> str | None:
    """Extract normalized host from absolute URL."""
    if not value or value.startswith('/'):
        return None
    return _normalized_host(urlparse(value).netloc)


def _get_redirect_uri() -> str:
    """Return absolute redirect URI used in both authorization and token steps."""
    callback_url = _cfg('CALLBACK_URL')
    callback_url_dev = _cfg('CALLBACK_URL_DEV')
    callback_url_prod = _cfg('CALLBACK_URL_PROD')

    # Explicit callback URL is authoritative when provided.
    if callback_url and not callback_url.startswith('/'):
        return callback_url

    request_host = _normalized_host(request.host)
    callback_url_dev_host = _url_host(callback_url_dev)
    callback_url_prod_host = _url_host(callback_url_prod)

    if request_host and callback_url_dev and request_host == callback_url_dev_host and not callback_url_dev.startswith('/'):
        return callback_url_dev
    if request_host and callback_url_prod and request_host == callback_url_prod_host and not callback_url_prod.startswith('/'):
        return callback_url_prod

    # For unrecognized hosts, do not trust host header to choose environment.
    if callback_url_prod and not callback_url_prod.startswith('/'):
        return callback_url_prod
    if callback_url_dev and not callback_url_dev.startswith('/'):
        return callback_url_dev

    return url_for('main.oauth_callback', _external=True)


@bp.get('/') # type: ignore
async def main() -> ResponseReturnValue:
    """Main function to run the application."""
    return render_template('index.html') # type: ignore


@bp.get('/about') # type: ignore
async def about() -> ResponseReturnValue:
    """About page."""
    return render_template('about.html') # type: ignore

  
@bp.get('/services') # type: ignore
async def services() -> ResponseReturnValue:
    """Services page."""
    return render_template('index.html') # type: ignore


@bp.get('/experience') # type: ignore
async def experience() -> ResponseReturnValue:
    """Work Experience page."""
    return render_template('index.html') # type: ignore


@bp.get('/portfolio') # type: ignore
async def portfolio() -> ResponseReturnValue:
    """Portfolio page."""
    return render_template('index.html') # type: ignore


@bp.get('/contact') # type: ignore
async def contact() -> ResponseReturnValue:
    """Contact page."""
    return render_template('index.html') # type: ignore


@bp.get('/fetch/github_metadata') # type: ignore
async def fetch_github_metadata() -> ResponseReturnValue:
    """Start GitHub OAuth flow and redirect user to authorization endpoint."""
    client_id = _cfg('CLIENT_ID')
    authorization_url = _cfg('AUTHORIZATION_URL')
    token_url = _cfg('TOKEN_URL')
    scope = _cfg('SCOPE')

    if not client_id or not authorization_url or not token_url:
        return ("OAuth configuration is incomplete on the server", 500) # type: ignore

    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    redirect_uri = _get_redirect_uri()

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state
    }

    if scope:
        params['scope'] = scope

    auth_url = f"{authorization_url}?{httpx.QueryParams(params)}"
    return redirect(auth_url)


@bp.get(OAUTH_CALLBACK_PATH) # type: ignore
async def oauth_callback() -> ResponseReturnValue:
    """Handle OAuth callback, exchange code, and fetch GitHub user metadata."""
    client_id = _cfg('CLIENT_ID')
    token_url = _cfg('TOKEN_URL')
    client_secret_obj = cast(dict[str, Any], current_app.config).get('CLIENT_SECRET')
    client_secret = client_secret_obj.strip() if isinstance(client_secret_obj, str) else None

    if not client_id or not token_url or not client_secret:
        return ("OAuth configuration is incomplete on the server", 500) # type: ignore

    code = request.args.get('code')
    state = request.args.get('state')
    oauth_error = request.args.get('error')
    oauth_error_description = request.args.get('error_description')
    expected_state = session.pop('oauth_state', None)

    # Validate state parameter first (CSRF protection) before processing any other callback parameters.
    if not state or not expected_state or state != expected_state:
        return ("Invalid state parameter", 400) # type: ignore

    if oauth_error:
        LOGGER.warning(
            "OAuth callback returned error from provider",
            extra={
                "oauth_error": oauth_error,
                "oauth_error_description": oauth_error_description,
                "request_host": request.host,
            },
        )
        return ("OAuth authorization failed", 400) # type: ignore

    if not code:
        return ("Missing OAuth authorization code", 400) # type: ignore

    redirect_uri = _get_redirect_uri()

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post(
                token_url,
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri
                },
                headers={'Accept': 'application/json'}
            )

            if token_response.is_error:
                LOGGER.warning(
                    "Token endpoint returned an error",
                    extra={
                        "status_code": token_response.status_code,
                        "request_host": request.host,
                    },
                )
                return ("Token exchange failed", 400) # type: ignore

            try:
                token_payload_obj = token_response.json()
            except ValueError:
                LOGGER.warning(
                    "Token endpoint returned invalid JSON",
                    extra={
                        "status_code": token_response.status_code,
                        "request_host": request.host,
                    },
                )
                return ("Token exchange failed", 502) # type: ignore

            if not isinstance(token_payload_obj, dict):
                LOGGER.warning(
                    "Token endpoint returned unexpected payload type",
                    extra={
                        "payload_type": type(token_payload_obj).__name__,
                        "request_host": request.host,
                    },
                )
                return ("Token exchange failed", 502) # type: ignore

            token_payload = cast(dict[str, Any], token_payload_obj)
            access_token_obj = token_payload.get('access_token')
            access_token = access_token_obj.strip() if isinstance(access_token_obj, str) else None

            if not access_token:
                error = token_payload.get('error', 'unknown_error')
                description = token_payload.get('error_description', 'No error description provided by GitHub')
                LOGGER.warning(
                    "Access token missing from token response",
                    extra={
                        "error": error,
                        "error_description": description,
                        "response_payload": token_payload,
                        "request_host": request.host,
                    },
                )
                return ("Token exchange failed", 400) # type: ignore

            # Fetch GitHub metadata using the access token.
            github_response = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {access_token}'}
            )
            github_response.raise_for_status()

            try:
                github_user_metadata_obj = github_response.json()
            except ValueError:
                LOGGER.warning(
                    "GitHub user endpoint returned invalid JSON",
                    extra={
                        "status_code": github_response.status_code,
                        "request_host": request.host,
                    },
                )
                return ("Failed to fetch GitHub metadata", 502) # type: ignore

            if not isinstance(github_user_metadata_obj, dict):
                LOGGER.warning(
                    "GitHub user endpoint returned unexpected payload type",
                    extra={
                        "payload_type": type(github_user_metadata_obj).__name__,
                        "request_host": request.host,
                    },
                )
                return ("Failed to fetch GitHub metadata", 502) # type: ignore

            github_user_metadata = cast(dict[str, Any], github_user_metadata_obj)
            github_username_obj = github_user_metadata.get('login')
            github_email_obj = github_user_metadata.get('email')
            github_username = github_username_obj if isinstance(github_username_obj, str) else None
            github_email = github_email_obj if isinstance(github_email_obj, str) else None
    except httpx.HTTPStatusError as exc:
        LOGGER.warning(
            "GitHub user endpoint returned HTTP error",
            extra={
                "status_code": exc.response.status_code,
                "request_host": request.host,
            },
        )
        return ("Failed to fetch GitHub metadata", 502) # type: ignore
    except httpx.RequestError as exc:
        LOGGER.warning(
            "OAuth upstream request failed",
            extra={
                "error": str(exc),
                "request_host": request.host,
            },
        )
        return ("OAuth upstream request failed", 502) # type: ignore
    return render_template('github_metadata.html', username=github_username, email=github_email, data=github_user_metadata) # type: ignore
