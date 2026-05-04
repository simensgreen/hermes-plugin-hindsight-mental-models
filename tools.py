"""Tool handlers for Hindsight mental model lookup."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_TIMEOUT_SECONDS = 20
VALID_DETAIL = {"metadata", "content", "full"}


def hindsight_get_mental_model(args: dict, **_kwargs) -> str:
    """Return one mental model by bank_id and model_id."""
    try:
        bank_id = _clean_required(args, "bank_id")
        model_id = _clean_required(args, "model_id")
        detail = _clean_detail(args.get("detail"), default="content")

        path = (
            f"/v1/default/banks/{_quote(bank_id)}/mental-models/"
            f"{_quote(model_id)}"
        )
        payload = _request_json(path, {"detail": detail})
        return _json(
            {
                "ok": True,
                "bank_id": bank_id,
                "model_id": model_id,
                "detail": detail,
                "mental_model": _compact_mental_model(payload, detail),
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": str(exc)})


def hindsight_list_mental_models(args: dict, **_kwargs) -> str:
    """Return mental models available in a bank."""
    try:
        bank_id = _clean_required(args, "bank_id")
        detail = _clean_detail(args.get("detail"), default="metadata")

        path = f"/v1/default/banks/{_quote(bank_id)}/mental-models"
        payload = _request_json(path, {"detail": detail})
        items = payload.get("items", payload if isinstance(payload, list) else [])
        if not isinstance(items, list):
            items = []

        compact_items = [_compact_mental_model(item, detail) for item in items]
        return _json(
            {
                "ok": True,
                "bank_id": bank_id,
                "detail": detail,
                "count": len(compact_items),
                "items": compact_items,
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": str(exc)})


def _request_json(path: str, query: dict[str, str] | None = None) -> Any:
    base_url = os.getenv("HINDSIGHT_API_URL", "").strip().rstrip("/")
    if not base_url:
        raise ValueError("HINDSIGHT_API_URL is not configured")

    url = base_url + path
    if query:
        url += "?" + urllib.parse.urlencode(query)

    headers = {
        "Accept": "application/json",
        "User-Agent": "hermes-plugin-hindsight-mental-models/0.1.0",
    }

    api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Hindsight HTTP {exc.code}: {body[:1000]}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Hindsight request failed: {exc}")

    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Hindsight returned non-JSON response: {exc}")


def _compact_mental_model(item: Any, detail: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"raw": item}

    result: dict[str, Any] = {
        "id": item.get("id"),
        "bank_id": item.get("bank_id"),
        "name": item.get("name"),
        "tags": item.get("tags"),
        "last_refreshed_at": item.get("last_refreshed_at"),
        "created_at": item.get("created_at"),
    }

    if detail in {"content", "full"}:
        result.update(
            {
                "source_query": item.get("source_query"),
                "content": item.get("content"),
                "max_tokens": item.get("max_tokens"),
                "trigger": item.get("trigger"),
            }
        )

    if detail == "full":
        # Keep provenance available for debugging, but avoid accidental giant payloads.
        reflect_response = item.get("reflect_response")
        if reflect_response is not None:
            result["reflect_response"] = reflect_response

    # Drop keys whose value is None for a smaller payload.
    return {key: value for key, value in result.items() if value is not None}


def _clean_required(args: dict, key: str) -> str:
    value = str(args.get(key) or "").strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _clean_detail(value: Any, default: str) -> str:
    detail = str(value or default).strip().lower()
    if detail not in VALID_DETAIL:
        raise ValueError(
            f"detail must be one of {sorted(VALID_DETAIL)}, got {detail!r}"
        )
    return detail


def _quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def _json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
