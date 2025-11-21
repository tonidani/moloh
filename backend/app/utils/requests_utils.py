import base64
from typing import Dict
from fastapi import Request
import json


async def extract_body_any(request: Request) -> Dict[str, str] | None:
    raw = await request.body()

    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        pass

    try:
        text = raw.decode("utf-8")
        return {"_text": text}
    except Exception:
        pass

    return {
        "_binary_base64": base64.b64encode(raw).decode("ascii"),
        "_size": len(raw)  # type: ignore
    }  # type: ignore
