from typing import Any, Dict
import jwt

from fastapi import HTTPException, Request
from app.variables import SECRET
from app.models.requests import RequestValidator
from app.utils.requests_utils import extract_body_any


async def get_db(request: Request):
    return request.app.state.db


async def get_redis(request: Request):
    return request.app.state.redis


async def extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if auth:
        if auth.startswith("Bearer "):
            return auth.split(" ", 1)[1]
        if len(auth.split()) == 1:
            return auth.strip()

    for hdr in ("X-Auth-Token", "X-Token", "X-Access-Token", "Authentication", "Bearer", "Token"):
        if hdr in request.headers:
            raw = request.headers.get(hdr)
            if raw.startswith("Bearer "):  # type: ignore
                return raw.split(" ", 1)[1]  # type: ignore
            return raw.strip()  # type: ignore

    q = request.query_params
    for key in ("token", "access_token"):
        if key in q:
            return q[key]

    return None


async def token_required(request: Request) -> Dict[str, Any]:
    token = await extract_token(request)

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS512"])  # type:ignore
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


async def validate_request(full_path: str, request: Request) -> RequestValidator:

    body = None
    if request.method in ("POST", "PUT", "PATCH"):
        body = await extract_body_any(request)

    return RequestValidator(
        client_ip=str(request.client.host),  # type: ignore
        full_path=full_path,
        method=request.method,
        query_params=dict(request.query_params),
        body=body,
        headers=dict(request.headers)
    )
