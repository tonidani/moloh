from typing import Any
import orjson

from app.models.interaction import InteractionCreate


class InteractionService:
    def __init__(self, db: Any):
        self.db = db

    async def save(self, interaction: InteractionCreate):
        request = interaction.request

        await self.db.execute(
            """
            INSERT INTO interactions(
                client_ip, method, path, query_params, semantic_key,
                headers_json, request_body, response_body,
                response_status, requested_at, response_headers
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.client_ip,
                request.method,
                request.full_path,
                orjson.dumps(request.query_params),
                request.semantic_key,
                orjson.dumps(request.headers),
                interaction.normalize_value(request.body),
                interaction.normalize_value(interaction.response_body),
                interaction.response_status,
                request.requested_at,
                interaction.normalize_value(interaction.response_headers)
            ),
        )

        await self.db.commit()
