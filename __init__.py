import base64
import json
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
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
SCOPE = os.getenv('SCOPE')
AUTHORIZATION_URL = os.getenv('AUTHORIZATION_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
CALLBACK_URL = os.getenv('CALLBACK_URL')
CALLBACK_URL_DEV = os.getenv('CALLBACK_URL_DEV')
CALLBACK_URL_PROD = os.getenv('CALLBACK_URL_PROD')


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
    """Resolve the GitHub client secret from AWS Secrets Manager, file, or Docker secret."""
    aws_secret_id = os.getenv('AWS_SECRETSMANAGER_SECRET_ID')
    aws_secret_key = os.getenv('AWS_SECRETSMANAGER_SECRET_KEY', 'client_secret')
    aws_region = os.getenv('AWS_REGION')

    if aws_secret_id:
        try:
            import boto3  # type: ignore
            client = boto3.client('secretsmanager', region_name=aws_region)
            response = client.get_secret_value(SecretId=aws_secret_id)
        except ImportError as exc:
            raise RuntimeError('boto3 is required to fetch secrets from AWS Secrets Manager') from exc
        except Exception as exc:
            raise RuntimeError('Failed to fetch client secret from AWS Secrets Manager') from exc

        secret_string = response.get('SecretString')
        if secret_string is None:
            secret_binary = response.get('SecretBinary')
            if not secret_binary:
                raise RuntimeError('AWS Secrets Manager response did not contain SecretString or SecretBinary')
            secret_string = base64.b64decode(secret_binary).decode('utf-8')

        try:
            secret_payload = json.loads(secret_string)
        except json.JSONDecodeError:
            return secret_string.strip()

        if isinstance(secret_payload, dict):
            secret_value = secret_payload.get(aws_secret_key)
            if not secret_value:
                raise RuntimeError(f"AWS secret JSON missing '{aws_secret_key}' field")
            return str(secret_value).strip()

        return str(secret_payload).strip()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    app.secret_key = _get_flask_secret_key()
    app.config["SECRET_KEY"] = app.secret_key
    app.config["CLIENT_ID"] = CLIENT_ID
    app.config["SCOPE"] = SCOPE
    app.config["AUTHORIZATION_URL"] = AUTHORIZATION_URL
    app.config["TOKEN_URL"] = TOKEN_URL
    app.config["CALLBACK_URL"] = CALLBACK_URL
    app.config["CALLBACK_URL_DEV"] = CALLBACK_URL_DEV
    app.config["CALLBACK_URL_PROD"] = CALLBACK_URL_PROD

    client_secret = _get_client_secret()
    app.config["CLIENT_SECRET"] = client_secret
    bootstrap.init_app(app) # type: ignore
    from main import bp
    app.register_blueprint(bp)
    return app
