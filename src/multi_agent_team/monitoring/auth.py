import os
import time
import json
import hmac
import hashlib
import base64
import secrets
from typing import Dict as _dict
from .config import settings


def _get_jwt_secret() -> str:
    return (
        settings.jwt_secret
        or os.getenv('MONITORING_JWT_SECRET')
        or settings.api_key
        or os.getenv('MONITORING_API_KEY')
        or 'dev-secret-key'
    )

_AUTO_SECRET = os.getenv('MONITORING_JWT_SECRET') or secrets.token_hex(32)


def _get_secret() -> str:
    return os.getenv('MONITORING_JWT_SECRET') or _AUTO_SECRET


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def create_jwt(claims: dict, exp_seconds: int = 3600) -> str:
    secret = _get_jwt_secret()
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = dict(claims)
    payload.setdefault('iat', int(time.time()))
    payload.setdefault('exp', int(time.time()) + exp_seconds)
    payload_s = _b64url(json.dumps(payload).encode())
    signing_input = f"{header}.{payload_s}".encode()
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{header}.{payload_s}.{_b64url(sig)}"


def verify_jwt(token: str) -> dict:
    secret = _get_jwt_secret()
    try:
        header_b64, payload_b64, sig_b64 = token.split('.')
    except Exception:
        raise ValueError('invalid token')
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    sig = _b64url_decode(sig_b64)
    if not hmac.compare_digest(expected, sig):
        raise ValueError('invalid signature')
    payload = json.loads(_b64url_decode(payload_b64))
    now = int(time.time())
    if 'exp' in payload and now >= int(payload['exp']):
        raise ValueError('token expired')
    return payload
