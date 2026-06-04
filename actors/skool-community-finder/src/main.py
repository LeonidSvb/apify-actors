"""
Skool Community Finder
Discovers Skool communities by keyword using DuckDuckGo search + __NEXT_DATA__ probing.
No login or cookies required — works with public communities only.
"""
import asyncio
import os
import re

import httpx
from apify import Actor

from .utils import (
    ACTOR_NAME,
    BROWSER_HEADERS,
    DDG_HEADERS,
    SYSTEM_SLUGS,
    build_meta,
    classify_access,
    extract_post_dates,
    parse_next_data,
)

PPE_EVENT = "community-found"

# Max slugs to probe = limit * PROBE_MULTIPLIER
# Accounts for failed probes and minMembers filtering
PROBE_MULTIPLIER = 4

# Delays to avoid blocks
DDG_DELAY_S = 3.5
SKOOL_DELAY_S = 0.7


async def ddg_search_slugs(keyword: str, timeout: int) -> list[str]:
    """Search DuckDuckGo for site:skool.com + keyword, return slug list."""
    query = f"site:skool.com {keyword}"
    encoded = query.replace(" ", "+").replace(":", "%3A")
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        async with httpx.AsyncClient(
            headers=DDG_HEADERS,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            html = resp.text
    except Exception as exc:
        Actor.log.warning(f"DDG search failed for '{keyword}': {exc}")
        return []

    slugs = re.findall(r'skool\.com/([a-z0-9\-]{3,50})(?:[/"\\s?])', html)
    return [
        s for s in dict.fromkeys(slugs)  # dedup, preserve order
        if s not in SYSTEM_SLUGS and not s.startswith("api")
    ]


async def probe_community(
    slug: str,
    proxy_url: str | None,
    timeout: int,
) -> dict | None:
    """
    Fetch skool.com/{slug} and extract community data from __NEXT_DATA__.
    Returns None if the page is not a valid community or is inaccessible.
    Always returns null for missing fields (never omits a key).
    """
    url = f"https://www.skool.com/{slug}"
    try:
        async with httpx.AsyncClient(
            headers=BROWSER_HEADERS,
            timeout=timeout,
            follow_redirects=True,
            proxy=proxy_url,
        ) as client:
            resp = await client.get(url)
    except Exception as exc:
        Actor.log.warning(f"probe({slug}): {exc}")
        return None

    if resp.status_code != 200:
        Actor.log.info(f"probe({slug}): HTTP {resp.status_code}")
        return None

    html = resp.text
    if "__NEXT_DATA__" not in html:
        return None

    data = parse_next_data(html)
    props = data.get("props", {}).get("pageProps", {})
    cg = props.get("currentGroup", {})
    meta = cg.get("metadata", {})

    name = meta.get("displayName") or cg.get("name") or ""
    gid = cg.get("id", "")
    if not name or not gid:
        return None

    desc = meta.get("description") or ""
    members_raw = meta.get("totalMembers") or meta.get("memberCount") or 0
    member_count = int(members_raw) if str(members_raw).isdigit() else 0
    is_member = "postTrees" in props

    # Pricing
    price_obj = meta.get("currentOtBp") or {}
    if isinstance(price_obj, str):
        try:
            import json as _json
            price_obj = _json.loads(price_obj)
        except Exception:
            price_obj = {}
    price_usd = (
        round(price_obj.get("amount", 0) / 100, 2)
        if isinstance(price_obj, dict)
        else 0.0
    )

    # Activity from postTrees (visible for public communities without login)
    post_trees = props.get("postTrees") or []
    last_post_date, days_since_last_post = extract_post_dates(post_trees)

    total_posts = int(meta.get("totalPosts") or 0)
    activity_ratio = round(total_posts / member_count, 4) if member_count > 0 else 0.0

    # Bonus: harvest suggestedCommunities while we have the page
    suggested = []
    for s in props.get("suggestedCommunities", []):
        sm = s.get("metadata", {})
        s_slug = s.get("name", "")
        if s_slug and s.get("id") and s_slug not in SYSTEM_SLUGS:
            suggested.append({"slug": s_slug, "name": sm.get("displayName") or s_slug})

    return {
        # Core identity
        "slug": slug,
        "url": url,
        "group_id": gid,
        "name": str(name),
        "description": str(desc)[:400] if desc else None,
        # Size & access
        "member_count": member_count,
        "online_members": int(meta.get("totalOnlineMembers") or 0),
        "access": classify_access(meta, is_member),
        "price_usd": price_usd,
        "has_survey": bool(meta.get("surveyEnabled") == 1),
        # Content
        "total_posts": total_posts,
        "num_courses": int(meta.get("numCourses") or 0),
        # Computed fields
        "activity_ratio": activity_ratio,
        "last_post_date": last_post_date,
        "days_since_last_post": days_since_last_post,
        # Internal only — stripped before push
        "_suggested": suggested,
    }


async def main() -> None:
    async with Actor:
        run_id = os.environ.get("APIFY_ACTOR_RUN_ID") or "local"

        # ── 1. Input & validation ────────────────────────────────────────────
        inp = await Actor.get_input() or {}

        keywords: list = inp.get("keywords") or []
        limit: int = min(int(inp.get("limit") or 50), 200)
        min_members: int = max(0, int(inp.get("minMembers") or 0))
        timeout: int = max(10, int(inp.get("requestTimeout") or 30))
        proxy_raw: dict = inp.get("proxyConfiguration") or {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        }

        if not keywords or not isinstance(keywords, list):
            await Actor.fail(
                status_message=(
                    "Input error: 'keywords' must be a non-empty array of strings. "
                    "Example: [\"cold email\", \"online course\"]"
                )
            )
            return

        keywords = [str(k).strip() for k in keywords if str(k).strip()]
        if not keywords:
            await Actor.fail(
                status_message="Input error: all keywords are empty strings."
            )
            return

        # ── 2. Proxy ─────────────────────────────────────────────────────────
        proxy_configuration = None
        try:
            proxy_configuration = await Actor.create_proxy_configuration(
                actor_proxy_input=proxy_raw
            )
        except Exception as exc:
            Actor.log.warning(f"Proxy unavailable: {exc}. Running without proxy (local test mode).")

        # ── 3. DDG phase: collect slug candidates ────────────────────────────
        await Actor.set_status_message(
            f"Searching DuckDuckGo for {len(keywords)} keyword(s)..."
        )

        slug_to_source: dict[str, str] = {}
        ddg_zero_streak = 0

        for keyword in keywords:
            Actor.log.info(f"DDG search: '{keyword}'")
            slugs = await ddg_search_slugs(keyword, timeout=timeout)

            new_slugs = [s for s in slugs if s not in slug_to_source]
            for s in new_slugs:
                slug_to_source[s] = f"ddg:{keyword}"

            Actor.log.info(f"  '{keyword}': {len(slugs)} slugs ({len(new_slugs)} new)")

            if not new_slugs:
                ddg_zero_streak += 1
            else:
                ddg_zero_streak = 0

            if ddg_zero_streak >= 3:
                Actor.log.warning(
                    "DDG returned 0 results for 3 consecutive keywords — "
                    "possible rate limiting. Proceeding with slugs found so far."
                )
                break

            if len(keywords) > 1:
                await asyncio.sleep(DDG_DELAY_S)

        total_slugs = len(slug_to_source)
        Actor.log.info(f"DDG phase complete: {total_slugs} unique slugs to probe")

        if total_slugs == 0:
            await Actor.fail(
                status_message=(
                    "DuckDuckGo returned no Skool URLs for the given keywords. "
                    "DuckDuckGo may be temporarily rate-limiting this IP. "
                    "Try again in a few minutes or use different keywords."
                )
            )
            return

        # ── 4. Probe phase: fetch each slug ──────────────────────────────────
        results: list[dict] = []
        seen_slugs: set[str] = set()
        extra_suggested: dict[str, str] = {}  # slug -> name

        probe_cap = min(total_slugs, limit * PROBE_MULTIPLIER)
        slugs_to_probe = list(slug_to_source.keys())[:probe_cap]

        await Actor.set_status_message(
            f"Found {total_slugs} slugs, probing up to {probe_cap}..."
        )

        for i, slug in enumerate(slugs_to_probe):
            if len(results) >= limit:
                break

            seen_slugs.add(slug)

            if i > 0 and i % 10 == 0:
                await Actor.set_status_message(
                    f"Probed {i}/{probe_cap} — {len(results)} communities found so far"
                )
                Actor.log.info(f"Progress: {i}/{probe_cap} probed, {len(results)} results")

            proxy_url = await proxy_configuration.new_url() if proxy_configuration else None
            community = await probe_community(slug, proxy_url=proxy_url, timeout=timeout)

            if community is None:
                await asyncio.sleep(SKOOL_DELAY_S)
                continue

            # Harvest suggested for later
            for sg in community.pop("_suggested", []):
                if sg["slug"] not in seen_slugs and sg["slug"] not in extra_suggested:
                    extra_suggested[sg["slug"]] = sg["name"]

            if community["member_count"] < min_members:
                await asyncio.sleep(SKOOL_DELAY_S)
                continue

            community["source"] = slug_to_source.get(slug, "ddg")
            results.append(community)

            await Actor.push_data({**community, "_meta": build_meta(run_id, len(results))})
            await Actor.charge(event_name=PPE_EVENT, count=1)

            await asyncio.sleep(SKOOL_DELAY_S)

        # ── 5. Suggested phase: bonus discovery ──────────────────────────────
        if len(results) < limit and extra_suggested:
            remaining = limit - len(results)
            # Sort by name length as crude quality signal (longer = more descriptive)
            suggested_slugs = [
                s for s in extra_suggested
                if s not in seen_slugs
            ][:remaining * 3]

            if suggested_slugs:
                await Actor.set_status_message(
                    f"Probing {len(suggested_slugs)} suggested communities..."
                )
                Actor.log.info(
                    f"Suggested phase: {len(suggested_slugs)} slugs from recommendations"
                )

            for slug in suggested_slugs:
                if len(results) >= limit:
                    break

                seen_slugs.add(slug)
                proxy_url = await proxy_configuration.new_url() if proxy_configuration else None
                community = await probe_community(slug, proxy_url=proxy_url, timeout=timeout)

                if community is None:
                    await asyncio.sleep(SKOOL_DELAY_S)
                    continue

                community.pop("_suggested", None)

                if community["member_count"] < min_members:
                    await asyncio.sleep(SKOOL_DELAY_S)
                    continue

                community["source"] = "suggested"
                results.append(community)

                await Actor.push_data({**community, "_meta": build_meta(run_id, len(results))})
                await Actor.charge(event_name=PPE_EVENT, count=1)

                await asyncio.sleep(SKOOL_DELAY_S)

        # ── 6. Final check ───────────────────────────────────────────────────
        if not results:
            await Actor.fail(
                status_message=(
                    f"No communities found matching your criteria "
                    f"(keywords: {keywords}, minMembers: {min_members}). "
                    "Try broader keywords, lower minMembers, or check the Issues tab."
                )
            )
            return

        await Actor.set_status_message(f"Done. Found {len(results)} communities.")
        Actor.log.info(
            f"Finished: {len(results)} communities from {len(seen_slugs)} probed slugs"
        )
