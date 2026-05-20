"""
Main entry point for the Python application.
"""
import os
import keyring
import secrets
import httpx
from urllib.parse import urlparse
from flask import request, render_template, Blueprint, redirect, session, url_for, current_app


bp = Blueprint("main", __name__)
CLIENT_ID = os.getenv('CLIENT_ID')
SCOPE = os.getenv('SCOPE')
AUTHORIZATION_URL = os.getenv('AUTHORIZATION_URL')
CALLBACK_URL = os.getenv('CALLBACK_URL')
KEYRING_SERVICE = os.getenv('KEYRING_SERVICE')
KEYRING_USERNAME = os.getenv('KEYRING_USERNAME')
TOKEN_URL = os.getenv('TOKEN_URL')


def _get_callback_route() -> str:
    """Return a valid route path for the OAuth callback endpoint."""
    if not CALLBACK_URL:
        return '/oauth/callback'
    if CALLBACK_URL.startswith('/'):
        return CALLBACK_URL
    parsed = urlparse(CALLBACK_URL)
    return parsed.path or '/oauth/callback'


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
    """OAuth callback endpoint."""
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': CALLBACK_URL,
        'scope': SCOPE,
        'state': state
    }

    auth_url = f"{AUTHORIZATION_URL}?{httpx.QueryParams(params)}"
    return redirect(auth_url)


@bp.get(_get_callback_route()) # type: ignore
async def oauth_callback() -> None:
    """OAuth callback endpoint."""
    # This function would handle the OAuth callback, exchange the code for an access token,
    # and fetch the GitHub metadata. The implementation is omitted for brevity.
    code = request.args.get('code')
    state = request.args.get('state')
    expected_state = session.get('oauth_state')
    if state != expected_state:
        return ("Invalid state parameter", 400) # type: ignore
    redirect_uri = url_for('main.oauth_callback', _external=True)

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                'client_id': CLIENT_ID,
                'client_secret': current_app.config['CLIENT_SECRET'],
                'code': code,
                'redirect_uri': redirect_uri
            },
            headers={'Accept': 'application/json'}
        )
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        if not access_token:
            return ("Failed to obtain access token", 400) # type: ignore

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
