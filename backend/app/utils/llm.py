from typing import Any, Dict, List
import httpx
import orjson

from app.models.llm import LLMResponse
from app.utils.attack_detector import detect_attack
from app.variables import OLLAMA_URL, MODEL, SYSTEM_PROMPT, AUGMENT_TEMPLATE, OPEN_API_KEY


async def call_llm(headers: dict, method: str, path: str, body: dict | None, query_params: dict | None) -> LLMResponse:  # type: ignore
    # faker_section = generate_faker_context(path)
    # system_prompt_final = SYSTEM_PROMPT + "\n\n" + faker_section

    attack_type, attack_template, dynamic_fields, emulated_files = detect_attack(
        method, path, query_params, body  # type: ignore
    )

    attack_section = ""
    dynamic_fields_section = ""
    emulated_files_section = ""

    if attack_type != "fallback":
        attack_section = f"""
            ATTACK_TYPE: {attack_type}
            ATTACK_BEHAVIOR:
            {attack_template}
        """

    if not OPEN_API_KEY:
        if dynamic_fields:
            dynamic_fields_section = f"""
                DYNAMIC_FIELDS (use for realism):
                {orjson.dumps(dynamic_fields)}
            """

    if emulated_files:
        emulated_files_section = f"""
            EMULATED_FILES (you may leak partial fragments if attack type allows it):
            {orjson.dumps(emulated_files)}
        """
    prompt = AUGMENT_TEMPLATE \
        .replace("{{method}}", str(method)) \
        .replace("{{headers}}", str(headers)) \
        .replace("{{path}}", str(path)) \
        .replace("{{body}}", str(body)) \
        .replace("{{query_params}}", str(query_params)) \
        .replace("{{attack_section}}", attack_section) \
        .replace("{{dynamic_fields_section}}", dynamic_fields_section) \
        .replace("{{emulated_files_section}}", emulated_files_section)

    headers: Dict[str, Any] | None = None
    url = f"{OLLAMA_URL}/api/chat"
    payload: Dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False
    }

    if OPEN_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",      # pewny, dostępny model
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {OPEN_API_KEY}",
            "Content-Type": "application/json",
        }

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        resp_json = r.json()

    if OPEN_API_KEY:
        data = resp_json["choices"][0]["message"]["content"]
    else:
        data = resp_json["message"]["content"]
    return LLMResponse.model_validate(data)


async def embed_text(text: str) -> List[float]:
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
        )
        return r.json()["embedding"]
