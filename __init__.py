import os
import secrets
from dotenv import load_dotenv
from flask import Flask
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


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    client_secret = _get_docker_secret("client_secret")
    app.config["CLIENT_SECRET"] = client_secret
    bootstrap.init_app(app) # type: ignore
    from main import bp
    app.register_blueprint(bp)
    return app
