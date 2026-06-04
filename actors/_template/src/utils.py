"""Shared utilities for all Skool actors."""
import re
from datetime import datetime, timezone


ACTOR_VERSION = "0.1.0"


def build_meta(actor_name: str, run_id: str, total_found: int) -> dict:
    return {
        "actor": actor_name,
        "version": ACTOR_VERSION,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_found": total_found,
        "run_id": run_id,
    }


def structured_error(error_type: str, message: str, retry: bool = False) -> dict:
    return {
        "error": error_type,
        "message": message,
        "retry": retry,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def validate_skool_url(url: str) -> bool:
    return bool(re.match(r"https?://www\.skool\.com/[\w-]+", url))


def days_ago(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return delta.days
    except (ValueError, TypeError):
        return None


def safe_get(d: dict, *keys, default=None):
    """Safely traverse nested dict without KeyError."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d
