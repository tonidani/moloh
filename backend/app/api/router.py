from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.resources import ResourceService
from app.dependencies import get_db, get_redis, token_required, validate_request, get_real_ip
from app.models.login import LoginRequest
from app.services.login import LoginService
from app.models.requests import RequestValidator

router = APIRouter()


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    db: Any = Depends(get_db),
    redis: Any = Depends(get_redis)
):
    return await LoginService(db, redis).login(data, get_real_ip(request.client.host))  # type: ignore


@router.get("/{full_path:path}")
async def get(
    full_path: str,
    request: RequestValidator = Depends(validate_request),
    db: Any = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    return await ResourceService(db, redis).get(request)


@router.post("/{full_path:path}")
async def post(
    full_path: str,
    request: RequestValidator = Depends(validate_request),
    db: Any = Depends(get_db),
    redis: Any = Depends(get_redis),
    token: Any = Depends(token_required),
):
    return await ResourceService(db, redis).crud(request, token)


@router.delete("/{full_path:path}")
async def delete(
    full_path: str,
    request: RequestValidator = Depends(validate_request),
    db: Any = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    return await ResourceService(db, redis).delete(request)
