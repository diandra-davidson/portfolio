import base64
import json
import os
import secrets
from typing import Any, cast
from dotenv import load_dotenv
from flask import Flask

from flask_bootstrap import Bootstrap5 # type: ignore


bootstrap = Bootstrap5() # type: ignore
load_dotenv()  # Load environment variables from .env file


CLIENT_ID = os.getenv('CLIENT_ID')
SCOPE = os.getenv('SCOPE')
AUTHORIZATION_URL = os.getenv('AUTHORIZATION_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
CALLBACK_URL = os.getenv('CALLBACK_URL')
CALLBACK_URL_DEV = os.getenv('CALLBACK_URL_DEV')
CALLBACK_URL_PROD = os.getenv('CALLBACK_URL_PROD')
AWS_SECRETSMANAGER_SECRET_NAME = os.getenv('AWS_SECRETSMANAGER_SECRET_NAME')
AWS_SECRETSMANAGER_REGION = os.getenv('AWS_SECRETSMANAGER_REGION')
AWS_SECRETSMANAGER_SERVICE_NAME = os.getenv('AWS_SECRETSMANAGER_SERVICE_NAME')
AWS_SECRETSMANAGER_FLASK_SERVICE_NAME = os.getenv('AWS_SECRETSMANAGER_FLASK_SERVICE_NAME')
AWS_SECRETSMANAGER_FLASK_SECRET_NAME = os.getenv('AWS_SECRETSMANAGER_FLASK_SECRET_NAME')
AWS_SECRETSMANAGER_FLASK_REGION = os.getenv('AWS_SECRETSMANAGER_FLASK_REGION')


def _get_secret_from_aws(secret_name: str, payload_key: str, aws_region: str) -> str:
    """Resolve a secret value from AWS Secrets Manager from plain or JSON payloads."""
    if not secret_name:
        raise RuntimeError('AWS_SECRETSMANAGER_SECRET_NAME is required')
    if not payload_key:
        raise RuntimeError('AWS_SECRETSMANAGER_SERVICE_NAME is required')
    if not aws_region:
        raise RuntimeError('AWS region is required')

    try:
        import boto3  # type: ignore
        client = boto3.client('secretsmanager', region_name=aws_region)  # type: ignore
        response = cast(dict[str, Any], client.get_secret_value(SecretId=secret_name))  # type: ignore
    except ImportError as exc:
        raise RuntimeError('boto3 is required to fetch secrets from AWS Secrets Manager') from exc
    except Exception as exc:
        raise RuntimeError('Failed to fetch secret from AWS Secrets Manager') from exc

    secret_string_obj = response.get('SecretString')
    if isinstance(secret_string_obj, str):
        secret_string = secret_string_obj
    else:
        secret_binary_obj = response.get('SecretBinary')
        if not secret_binary_obj:
            raise RuntimeError('AWS Secrets Manager response did not contain SecretString or SecretBinary')

        if isinstance(secret_binary_obj, str):
            secret_binary = secret_binary_obj.encode('utf-8')
        elif isinstance(secret_binary_obj, (bytes, bytearray)):
            secret_binary = bytes(secret_binary_obj)
        else:
            raise RuntimeError('AWS Secrets Manager returned unsupported SecretBinary type')
        secret_string = base64.b64decode(secret_binary).decode('utf-8')

    try:
        secret_payload_obj = json.loads(secret_string)
    except json.JSONDecodeError:
        stripped = secret_string.strip()
        if not stripped:
            raise RuntimeError('AWS secret value is empty')
        return stripped

    if not isinstance(secret_payload_obj, dict):
        raise RuntimeError('AWS secret JSON must be an object')

    typed_payload = cast(dict[str, Any], secret_payload_obj)
    secret_value_obj = typed_payload.get(payload_key)
    if not isinstance(secret_value_obj, str):
        raise RuntimeError(f"AWS secret JSON missing '{payload_key}' field")

    secret_value = secret_value_obj.strip()
    if not secret_value:
        raise RuntimeError(f"AWS secret JSON missing '{payload_key}' field")
    return secret_value


def _get_flask_secret_key() -> str:
    """Resolve Flask secret key from explicit env, AWS, or dev-safe fallback."""
    flask_secret_key_env = os.getenv('FLASK_SECRET_KEY')
    flask_secret_name = AWS_SECRETSMANAGER_FLASK_SECRET_NAME
    flask_service_name = AWS_SECRETSMANAGER_FLASK_SERVICE_NAME
    flask_region = AWS_SECRETSMANAGER_FLASK_REGION

    if flask_secret_key_env:
        stripped = flask_secret_key_env.strip()
        if stripped:
            return stripped

    has_any_flask_aws = any(
        [
            flask_secret_name,
            flask_service_name,
            flask_region,
        ]
    )

    if has_any_flask_aws:
        if not flask_secret_name:
            raise RuntimeError('AWS_SECRETSMANAGER_FLASK_SECRET_NAME is required')
        if not flask_service_name:
            raise RuntimeError('AWS_SECRETSMANAGER_FLASK_SERVICE_NAME is required')
        if not flask_region:
            raise RuntimeError('AWS_SECRETSMANAGER_FLASK_REGION is required')
        return _get_secret_from_aws(
            flask_secret_name,
            flask_service_name,
            flask_region,
        )

    return secrets.token_urlsafe(32)


def _get_client_secret() -> str:
    """Resolve GitHub OAuth client secret from AWS Secrets Manager."""
    secret_name = AWS_SECRETSMANAGER_SECRET_NAME
    payload_key = AWS_SECRETSMANAGER_SERVICE_NAME or 'client_secret'
    region = AWS_SECRETSMANAGER_REGION

    if not secret_name:
        raise RuntimeError('AWS_SECRETSMANAGER_SECRET_NAME is required')
    if not region:
        raise RuntimeError('AWS_REGION or AWS_SECRETSMANAGER_REGION is required')

    return _get_secret_from_aws(
        secret_name,
        payload_key,
        region,
    )


def _get_client_secrets() -> tuple[str, str]:
    """Return (flask_secret_key, github_client_secret)."""
    flask_secret_key = _get_flask_secret_key()
    client_secret = _get_client_secret()
    return flask_secret_key, client_secret


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    flask_secret_key, client_secret = _get_client_secrets()
    app.secret_key = flask_secret_key
    app.config["SECRET_KEY"] = app.secret_key
    app.config["CLIENT_ID"] = CLIENT_ID
    app.config["SCOPE"] = SCOPE
    app.config["AUTHORIZATION_URL"] = AUTHORIZATION_URL
    app.config["TOKEN_URL"] = TOKEN_URL
    app.config["CALLBACK_URL"] = CALLBACK_URL
    app.config["CALLBACK_URL_DEV"] = CALLBACK_URL_DEV
    app.config["CALLBACK_URL_PROD"] = CALLBACK_URL_PROD
    app.config["FLASK_SECRET_KEY"] = flask_secret_key
    app.config["CLIENT_SECRET"] = client_secret
    bootstrap.init_app(app) # type: ignore
    from main import bp
    app.register_blueprint(bp)
    return app
