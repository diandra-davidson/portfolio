"""
Main entry point for the Python application.
"""
import os
import secrets
import httpx
from urllib.parse import urlparse
from flask import request, render_template, Blueprint, redirect, session, url_for, current_app


bp = Blueprint("main", __name__)
OAUTH_CALLBACK_PATH = '/oauth/callback'


def _cfg(key: str) -> str | None:
    """Return OAuth-related config value from app config, then environment."""
    return current_app.config.get(key) or os.getenv(key)


def _get_redirect_uri() -> str:
    """Return absolute redirect URI used in both authorization and token steps."""
    callback_url = _cfg('CALLBACK_URL')
    callback_url_dev = _cfg('CALLBACK_URL_DEV')
    callback_url_prod = _cfg('CALLBACK_URL_PROD')

    # Explicit override wins in all environments.
    if callback_url and not callback_url.startswith('/'):
        return callback_url

    # Choose a callback URL based on the active host when explicit CALLBACK_URL is absent.
    host = request.host or ''
    if 'github.dev' in host and callback_url_dev:
        return callback_url_dev
    if 'github.dev' not in host and callback_url_prod:
        return callback_url_prod

    return url_for('main.oauth_callback', _external=True)


@bp.get('/') # type: ignore
async def main() -> None:
    """Main function to run the application."""
    return render_template('index.html') # type: ignore


@bp.get('/about') # type: ignore
async def about() -> None:
    """About page."""
    return render_template('about.html') # type: ignore

  
@bp.get('/services') # type: ignore
async def services() -> None:
    """Services page."""
    return render_template('index.html') # type: ignore


@bp.get('/experience') # type: ignore
async def experience() -> None:
    """Work Experience page."""
    return render_template('index.html') # type: ignore


@bp.get('/portfolio') # type: ignore
async def portfolio() -> None:
    """Portfolio page."""
    return render_template('index.html') # type: ignore


@bp.get('/contact') # type: ignore
async def contact() -> None:
    """Contact page."""
    return render_template('index.html') # type: ignore


@bp.get('/fetch/github_metadata') # type: ignore
async def fetch_github_metadata() -> None:
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
        'scope': scope,
        'state': state
    }

    auth_url = f"{authorization_url}?{httpx.QueryParams(params)}"
    return redirect(auth_url)


@bp.get(OAUTH_CALLBACK_PATH) # type: ignore
async def oauth_callback() -> None:
    """Handle OAuth callback, exchange code, and fetch GitHub user metadata."""
    client_id = _cfg('CLIENT_ID')
    token_url = _cfg('TOKEN_URL')

    if not client_id or not token_url:
        return ("OAuth configuration is incomplete on the server", 500) # type: ignore

    code = request.args.get('code')
    state = request.args.get('state')
    oauth_error = request.args.get('error')
    oauth_error_description = request.args.get('error_description')
    expected_state = session.pop('oauth_state', None)

    if oauth_error:
        return (f"OAuth error: {oauth_error}. {oauth_error_description or ''}".strip(), 400) # type: ignore

    if not code:
        return ("Missing OAuth authorization code", 400) # type: ignore

    if state != expected_state:
        return ("Invalid state parameter", 400) # type: ignore

    redirect_uri = _get_redirect_uri()

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            token_url,
            data={
                'client_id': client_id,
                'client_secret': current_app.config['CLIENT_SECRET'],
                'code': code,
                'redirect_uri': redirect_uri
            },
            headers={'Accept': 'application/json'}
        )

        if token_response.is_error:
            return (f"Token endpoint error {token_response.status_code}: {token_response.text}", 400) # type: ignore

        token_payload = token_response.json()
        access_token = token_payload.get('access_token')

        if not access_token:
            error = token_payload.get('error', 'unknown_error')
            description = token_payload.get('error_description', 'No error description provided by GitHub')
            return (f"Failed to obtain access token: {error}. {description}", 400) # type: ignore

        # Fetch GitHub metadata using the access token
        github_response = await client.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        )
        github_response.raise_for_status()
        github_user_metadata = github_response.json()
        github_username = github_user_metadata.get('login')
        github_email = github_user_metadata.get('email')
    return render_template('github_metadata.html', username=github_username, email=github_email, data=github_user_metadata) # type: ignore
