"""Shared utilities for skool-community-finder."""
import json
import re
from datetime import date, datetime, timezone

ACTOR_NAME = "skool-community-finder"
ACTOR_VERSION = "0.1.0"

SYSTEM_SLUGS = {
    "home", "login", "signup", "about", "pricing", "search",
    "discover", "profile", "settings", "terms", "privacy", "blog",
    "affiliate", "contact", "help", "support", "careers", "jobs",
    "api", "auth", "oauth", "static", "public", "assets",
}

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.skool.com/",
}

DDG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_next_data(html: str) -> dict:
    match = re.search(r"__NEXT_DATA__[^>]*>(.*?)</script>", html, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def classify_access(meta: dict, is_member: bool) -> str:
    if is_member:
        return "public"
    price_obj = meta.get("currentOtBp") or {}
    if isinstance(price_obj, str):
        try:
            price_obj = json.loads(price_obj)
        except Exception:
            price_obj = {}
    amount = price_obj.get("amount", 0) if isinstance(price_obj, dict) else 0
    if amount and int(amount) > 0:
        return "paid"
    if meta.get("invitation") == 1:
        return "invite_only"
    if meta.get("surveyEnabled") == 1:
        return "free_survey"
    return "free_open"


def extract_post_dates(post_trees: list) -> tuple[str | None, int | None]:
    """Return (last_post_date_iso, days_since_last_post) from postTrees array."""
    dates = []
    for tree in post_trees:
        post = tree.get("post", tree)
        created = post.get("createdAt") or post.get("created_at") or ""
        if created:
            dates.append(str(created)[:10])
    if not dates:
        return None, None
    newest = max(dates)
    try:
        days = (date.today() - date.fromisoformat(newest[:10])).days
    except (ValueError, TypeError):
        days = None
    return newest[:10], days


def build_meta(run_id: str, total_found: int) -> dict:
    return {
        "actor": ACTOR_NAME,
        "version": ACTOR_VERSION,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_found": total_found,
        "run_id": run_id,
    }
