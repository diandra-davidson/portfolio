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


FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
SCOPE = os.getenv('SCOPE')
AUTHORIZATION_URL = os.getenv('AUTHORIZATION_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
CALLBACK_URL = os.getenv('CALLBACK_URL')
CALLBACK_URL_DEV = os.getenv('CALLBACK_URL_DEV')
CALLBACK_URL_PROD = os.getenv('CALLBACK_URL_PROD')


def _get_flask_secret_key() -> str:
    """Resolve Flask session secret with a safe fallback for development."""
    if FLASK_SECRET_KEY:
        return FLASK_SECRET_KEY
    return secrets.token_urlsafe(32)


def _get_client_secret() -> str:
    """Resolve the GitHub client secret from AWS Secrets Manager."""
    aws_secret_name = os.getenv('AWS_SECRETSMANAGER_SECRET_NAME')
    aws_service_name = os.getenv('AWS_SECRETSMANAGER_SERVICE_NAME', 
                               'client_secret')
    aws_region = os.getenv('AWS_REGION')

    if not aws_secret_name:
        raise RuntimeError('AWS_SECRETSMANAGER_SECRET_NAME is required')
    if not aws_service_name:
        raise RuntimeError('AWS_SECRETSMANAGER_SERVICE_NAME is required')
    if not aws_region:
        raise RuntimeError('AWS_REGION is required')

    try:
        import boto3  # type: ignore
        client = boto3.client('secretsmanager', region_name=aws_region)  # type: ignore
        response = cast(dict[str, Any], client.get_secret_value(SecretId=aws_secret_name))  # type: ignore
    except ImportError as exc:
        raise RuntimeError('boto3 is required to fetch secrets from AWS Secrets Manager') from exc
    except Exception as exc:
        raise RuntimeError('Failed to fetch client secret from AWS Secrets Manager') from exc

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
        secret_payload = json.loads(secret_string)
    except json.JSONDecodeError:
        stripped = secret_string.strip()
        if not stripped:
            raise RuntimeError('AWS secret value is empty')
        return stripped

    if not isinstance(secret_payload, dict):
        raise RuntimeError('AWS secret JSON must be an object')

    typed_payload = cast(dict[str, Any], secret_payload)

    secret_value_obj = typed_payload.get(aws_service_name)
    if not isinstance(secret_value_obj, str):
        raise RuntimeError(f"AWS secret JSON missing '{aws_service_name}' field")

    secret_value = secret_value_obj.strip()

    if not secret_value:
        raise RuntimeError(f"AWS secret JSON missing '{aws_service_name}' field")
    return secret_value


def create_app() -> Flask:
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
