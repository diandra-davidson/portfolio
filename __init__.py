import os
import secrets
from dotenv import load_dotenv
from flask import Flask
from pathlib import Path

from flask_bootstrap import Bootstrap5 # type: ignore


bootstrap = Bootstrap5() # type: ignore
load_dotenv()  # Load environment variables from .env file


KEYRING_SERVICE_NAME = os.getenv('KEYRING_SERVICE_NAME')
KEYRING_USERNAME = os.getenv('KEYRING_USERNAME')
CLIENT_SECRET_FILE = os.getenv('CLIENT_SECRET_FILE')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')


def _get_docker_secret(secret_name: str) -> str:
    """Read a Docker secret from /run/secrets/"""
    secret_path = f"/run/secrets/{secret_name}"
    try:
        with open(secret_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"Docker secret '{secret_name}' not found at {secret_path}")


def _get_flask_secret_key() -> str:
    """Resolve Flask session secret with a safe fallback for development."""
    if FLASK_SECRET_KEY:
        return FLASK_SECRET_KEY
    return secrets.token_urlsafe(32)


def _get_client_secret() -> str:
    """Resolve the GitHub client secret from env vars or Docker secrets."""
    if os.getenv('CLIENT_SECRET'):
        return os.environ['CLIENT_SECRET']

    if CLIENT_SECRET_FILE:
        client_secret_path = Path(CLIENT_SECRET_FILE)
        if client_secret_path.exists():
            return client_secret_path.read_text(encoding='utf-8').strip()

    return _get_docker_secret("client_secret")


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    app.secret_key = _get_flask_secret_key()
    app.config["SECRET_KEY"] = app.secret_key

    client_secret = _get_client_secret()
    app.config["CLIENT_SECRET"] = client_secret
    bootstrap.init_app(app) # type: ignore
    from main import bp
    app.register_blueprint(bp)
    return app
