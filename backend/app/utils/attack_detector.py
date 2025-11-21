from typing import Any, Dict, Tuple
from app.variables import ATTACK_TEMPLATE


def detect_attack(
    method: str,
    path: str,
    query_params: Dict[str, Any] | None,
    body: Dict[str, Any] | None,
    attack_template: Dict[str, Any] | None = ATTACK_TEMPLATE,
) -> Tuple[str, str, Dict[str, Any], Dict[str, str]] | Tuple[None, None, None, None]:
    if attack_template is None:
        return None, None, None, None

    dynamic_fields = attack_template.get("dynamic_fields", {})
    emulated_files = attack_template.get("emulated_files", {}).get("files", {})

    haystack = " ".join([
        (method or ""),
        (path or ""),
        str(query_params or ""),
        str(body or "")
    ]).lower()

    best_key = None
    best_template = None
    best_score = -1

    for key, entry in attack_template.items():
        if key in ("dynamic_fields", "emulated_files", "fallback"):
            continue
        if not isinstance(entry, dict):
            continue
        if "patterns" not in entry or "template" not in entry:
            continue

        patterns = entry["patterns"]  # type: ignore
        score = sum(1 for p in patterns if p.lower() in haystack)  # type: ignore

        if score > best_score and score > 0:
            best_score = score
            best_key = key
            best_template = entry["template"]  # type: ignore

    if best_key is None:
        return None, None, None, None

    return best_key, best_template, dynamic_fields, emulated_files  # type: ignore
