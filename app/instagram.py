from __future__ import annotations

import logging
import os
from typing import Any

import httpx

GRAPH_API_URL = "https://graph.instagram.com/me/media"
logger = logging.getLogger(__name__)


def _fetch_graph_media(limit: int) -> list[dict[str, Any]]:
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
    if not token:
        return []

    fields = os.getenv(
        "INSTAGRAM_FIELDS",
        "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp",
    )

    params = {
        "fields": fields,
        "access_token": token,
        "limit": str(limit),
    }

    with httpx.Client(timeout=8.0) as client:
        response = client.get(GRAPH_API_URL, params=params)
        response.raise_for_status()

    payload = response.json()
    items: list[dict[str, Any]] = []

    for item in payload.get("data", []):
        media_type = (item.get("media_type") or "").upper()
        media_url = item.get("media_url")

        if media_type == "VIDEO":
            media_url = item.get("thumbnail_url") or media_url

        if not media_url:
            continue

        items.append(
            {
                "id": item.get("id"),
                "caption": item.get("caption") or "Latest Instagram post",
                "media_url": media_url,
                "permalink": item.get("permalink"),
                "timestamp": item.get("timestamp"),
                "media_type": media_type,
            }
        )

        if len(items) >= limit:
            break

    return items


def resolve_instagram_feed(content_data: dict[str, Any]) -> dict[str, Any]:
    instagram_cfg = content_data.get("instagram", {}) if isinstance(content_data, dict) else {}

    if not instagram_cfg.get("latest_enabled", False):
        return {"source": "disabled", "items": [], "embeds": []}

    limit = int(instagram_cfg.get("max_items", 4) or 4)

    try:
        graph_items = _fetch_graph_media(limit)
    except Exception as exc:  # pragma: no cover - network path
        logger.warning("Instagram Graph fetch failed; falling back to embed/manual mode: %s", exc)
        graph_items = []

    if graph_items:
        return {"source": "graph", "items": graph_items, "embeds": []}

    embeds = instagram_cfg.get("embeds") or []
    normalized_embeds: list[dict[str, str]] = []

    if isinstance(embeds, list):
        for entry in embeds[:limit]:
            if isinstance(entry, dict) and entry.get("html"):
                normalized_embeds.append(
                    {
                        "title": str(entry.get("title") or "Instagram post"),
                        "html": str(entry["html"]),
                    }
                )

    if normalized_embeds:
        return {"source": "embed", "items": [], "embeds": normalized_embeds}

    return {"source": "manual", "items": [], "embeds": []}
