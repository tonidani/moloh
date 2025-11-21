from typing import Any, List
import numpy as np
from fastapi.responses import HTMLResponse, JSONResponse, Response


from app.models.requests import RequestValidator
from app.models.resources import ResourceCreate, ResourceDB
from app.services.interactions import InteractionService
from app.models.interaction import InteractionCreate
from app.models.llm import DEFAULT_HEADERS
from app.redis_db import redis_lock
from app.utils.llm import embed_text, call_llm


class ResourceService:
    def __init__(self, db: Any, redis: Any):
        self.db = db
        self.redis = redis
        self.interaction_service = InteractionService(db)

    async def get(self, req: RequestValidator) -> Response:
        async with redis_lock(self.redis, req.hash):
            return await self._handle_get(req)

    async def crud(self, req: RequestValidator) -> Response:
        async with redis_lock(self.redis, req.hash):
            return await self._handle_crud(req)

    async def _handle_get(self, req: RequestValidator):
        embedding = await embed_text(req.semantic_key)
        canonical = req.canonicalize("GET")

        res = await self.find_resource(canonical, embedding, req.full_path)
        if res:
            interaction = InteractionCreate(
                request=req,
                response_body=res.response_body,
                response_status=res.response_status,
                response_headers=res.response_headers
            )
            await self.interaction_service.save(interaction)
            return self.respond(res.response_body, res.response_status, res.response_headers)

        limited, ttl = await self.rate_limit_new_get(req.client_ip)
        if limited:
            return JSONResponse(
                {"error": "Rate limit exceeded. Try again later.", "retry_after": ttl},
                status_code=429
            )

        # no match → call LLM
        llm_resp = await call_llm(
            req.headers, "GET", req.full_path, None, req.query_params
        )

        new_resource = ResourceCreate(
            path=req.full_path,
            canonical_key=canonical,
            response_body=llm_resp.body,
            response_status=llm_resp.status_code,
            response_headers=llm_resp.headers,
            embedding=embedding
        )

        await self.create(new_resource)

        interaction = InteractionCreate(
            request=req,
            response_body=llm_resp.body,
            response_status=llm_resp.status_code,
            response_headers=llm_resp.headers
        )
        await self.interaction_service.save(interaction)
        return self.respond(llm_resp.body, llm_resp.status_code, llm_resp.headers)

    async def _handle_crud(self, req: RequestValidator):
        canonical = req.canonicalize("GET")
        existing = await self.find_canonical(canonical)

        if not existing:
            resource = ResourceCreate(
                path=req.full_path,
                canonical_key=canonical,
                response_body=req.body,
                response_status=200,
                embedding=await embed_text(req.semantic_key),
            )
            await self.create(resource)

            interaction = InteractionCreate(
                request=req,
                response_body=req.body,
                response_status=200,
            )
            await self.interaction_service.save(interaction)

            return self.respond(interaction.response_body, 200)

        saved_body = existing.response_body
        if saved_body and isinstance(saved_body, dict):
            # JUST CAN JSON CHANGE, NOT HTML OR OTHERS
            for k in req.body.keys():
                if k not in saved_body and k not in ("id", "_id"):
                    return JSONResponse({"error": f"Unknown field: {k}"}, 400)

            new_body = saved_body | req.body
            await self.update(existing.id, new_body)

        new_body = req.body

        interaction = InteractionCreate(
            request=req,
            response_body=new_body,
            response_status=200,
            response_headers=existing.response_headers
        )
        await self.interaction_service.save(interaction)

        return self.respond(new_body, 200, existing.response_headers)

    async def find_resource(self, canonical_key: str, embedding: List[float], path: str):
        res = await self.find_by_path(path)
        if res:
            return res

        # 1) canonical
        res = await self.find_canonical(canonical_key)
        if res:
            return res

        # 2) vector search
        res = await self.find_vector(embedding)
        if res:
            return res

        return None

    async def find_by_path(self, path: str) -> ResourceDB | None:
        q = "SELECT id, response_body, response_status, response_headers FROM resources WHERE path = ?"
        async with self.db.execute(q, (path,)) as cur:
            row = await cur.fetchone()

        if not row:
            return None

        rid, body_raw, status, headers = row
        resource = {"id": rid, "response_body": body_raw, "response_status": status, "response_headers": headers}

        return ResourceDB.from_row(resource)

    async def find_canonical(self, canonical_key: str) -> ResourceDB | None:
        q = "SELECT id, response_body, response_status, response_headers FROM resources WHERE canonical_key = ?"
        async with self.db.execute(q, (canonical_key,)) as cur:
            row = await cur.fetchone()

        if not row:
            return None

        rid, body_raw, status, headers = row
        resource = {"id": rid, "response_body": body_raw, "response_status": status, "response_headers": headers}

        return ResourceDB.from_row(resource)

    async def find_vector(self, embedding: List[float], threshold: float = 0.8) -> ResourceDB | None:
        vec_blob = np.asarray(embedding, dtype=np.float32).tobytes()

        # 1) jeśli nie ma żadnych embeddingów — nie szukaj
        async with self.db.execute("SELECT COUNT(*) FROM embeddings") as cur:
            (count,) = await cur.fetchone()
            if count == 0:
                return None

        q = """
        SELECT r.id, r.response_body, r.response_status, v.distance, r.response_headers
        FROM (
            SELECT rowid, distance
            FROM embeddings
            WHERE vss_search(embedding, ?)
            LIMIT 1
        ) AS v
        JOIN resources r ON r.id = v.rowid;
        """

        async with self.db.execute(q, (vec_blob,)) as cur:
            row = await cur.fetchone()

        if not row:
            return None

        rid, body_raw, status, distance, headers = row

        similarity = 1 - float(distance)
        if similarity < threshold:
            return None

        resource = {"id": rid, "response_body": body_raw, "response_status": status, "response_headers": headers}

        return ResourceDB.from_row(resource)

    async def create(self, resource: ResourceCreate):
        insert_q, params = resource.get_insert_query()
        try:
            async with self.db.execute(insert_q, params) as cur:
                rid = cur.lastrowid

            await self.db.execute(
                "INSERT INTO embeddings (rowid, embedding) VALUES (?, ?)",
                (rid, resource.get_embedding_blob()),
            )
            await self.db.commit()
        except Exception as e:
            print("RESOURCE INSERT ERROR:", e)
            raise

    async def update(self, resource_id: int, body: Any):
        q = "UPDATE resources SET response_body = ? WHERE id = ?"
        blob = ResourceCreate(response_body=body, response_status=204).get_blob('response_body')
        await self.db.execute(q, (blob, resource_id))
        await self.db.commit()

    async def rate_limit_new_get(self, client_ip: str, limit: int = 10, window: int = 900):
        key = f"rate:newget:{client_ip}"

        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, window)

        if count > limit:
            ttl = await self.redis.ttl(key)
            return True, ttl

        return False, None

    def respond(self, body: Any, status=200, headers=DEFAULT_HEADERS) -> Response:
        clean = DEFAULT_HEADERS

        if isinstance(headers, dict):
            forbidden = {"content-length", "transfer-encoding", "date", "server"}

            clean = {}
            for k, v in headers.items():
                # pomiń zabronione
                key_lower = k.lower()
                if key_lower in forbidden or key_lower == "content-type":
                    continue

            clean[k] = str(v)

        # JSON dict
        if isinstance(body, dict):
            return JSONResponse(
                content=body,
                status_code=status,
                headers=clean
            )

        # HTML
        if isinstance(body, str) and "<html" in body.lower():
            return HTMLResponse(
                content=body,
                status_code=status,
                media_type="text/html",
                headers=clean
            )

        # plain text
        return Response(
            content=str(body),
            status_code=status,
            media_type="text/plain",
            headers=clean
        )
