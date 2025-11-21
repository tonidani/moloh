import time
import secrets
import jwt

from typing import Any, Dict
from fastapi import HTTPException
from app.models.login import LoginRequest
from app.variables import SECRET


class LoginService:
    def __init__(self, db: Any, redis: Any):
        self.db = db
        self.redis = redis

    async def login(self, data: LoginRequest, client_ip: str) -> Dict[str, str]:
        username = data.username

        async with self.db.execute("SELECT 1 FROM users WHERE username = ?", (username,)) as cur:
            exists = await cur.fetchone()

        if exists:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        await self.db.execute(
            "INSERT INTO users (username, password, client_ip) VALUES (?, ?, ?)",
            (username, data.password, client_ip)
        )
        await self.db.commit()

        if secrets.choice([True, False]) is False:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        payload: Dict[str, Any] = {
            "sub": username,
            "ip": client_ip,
            "iat": int(time.time()),
            "exp": int(time.time()) + 9000
        }

        token = jwt.encode(payload, SECRET, algorithm="HS512")  # type:ignore

        return {"access_token": token}
