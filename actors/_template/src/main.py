"""
{{ACTOR_TITLE}}
Replace this block with a one-line description of what the actor does.
"""
import asyncio
import httpx
from apify import Actor
from .utils import build_meta, structured_error, validate_skool_url, days_ago

ACTOR_NAME = "{{ACTOR_SLUG}}"
PPE_EVENT = "item-scraped"


async def main() -> None:
    async with Actor:
        run_id = Actor.config.actor_run_id or "local"

        # --- 1. Read and validate input ---
        inp = await Actor.get_input() or {}

        start_urls: list = inp.get("startUrls") or []
        limit: int = inp.get("limit", 50)
        request_timeout: int = inp.get("requestTimeout", 30)
        proxy_config_raw: dict = inp.get("proxyConfiguration", {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]})

        if not start_urls:
            await Actor.fail(
                status_message=(
                    "No startUrls provided. Please add at least one Skool community URL "
                    "like https://www.skool.com/community-name"
                )
            )
            return

        urls = [item.get("url", item) if isinstance(item, dict) else item for item in start_urls]
        invalid = [u for u in urls if not validate_skool_url(u)]
        if invalid:
            await Actor.fail(
                status_message=(
                    f"Invalid Skool URL(s): {invalid[:3]}. "
                    "URLs must match https://www.skool.com/community-name"
                )
            )
            return

        # --- 2. Configure proxy ---
        proxy_configuration = await Actor.create_proxy_configuration(
            actor_proxy_input=proxy_config_raw
        )

        # --- 3. Main scraping loop ---
        results: list[dict] = []
        total_urls = len(urls)

        for idx, url in enumerate(urls):
            if len(results) >= limit:
                break

            await Actor.set_status_message(
                f"Processing {idx + 1}/{total_urls}: {url.split('/')[-1]} "
                f"({len(results)} results so far)"
            )

            try:
                proxy_url = await proxy_configuration.new_url() if proxy_configuration else None
                items = await scrape_one(url, proxy_url=proxy_url, timeout=request_timeout)

                for item in items:
                    if len(results) >= limit:
                        break
                    results.append(item)
                    await Actor.push_data(item)
                    await Actor.charge(event_name=PPE_EVENT, count=1)

                Actor.log.info(f"Scraped {len(items)} items from {url}")

            except Exception as exc:
                Actor.log.error(f"Failed to scrape {url}: {exc}")
                await Actor.push_data(
                    structured_error("scrape_failed", f"Failed to scrape {url}: {exc}", retry=True)
                )

        # --- 4. Final status and health check ---
        if not results:
            await Actor.fail(
                status_message=(
                    "No results found. Possible causes: "
                    "community is private, residential proxy is required, "
                    "or Skool changed their page structure. "
                    "Check Issues tab for known problems."
                )
            )
            return

        await Actor.set_status_message(f"Done. Scraped {len(results)} items.")
        Actor.log.info(f"Finished: {len(results)} items from {total_urls} communities")


async def scrape_one(url: str, proxy_url: str | None, timeout: int) -> list[dict]:
    """Scrape a single Skool community URL. Replace with real implementation."""
    # TODO: implement actual scraping logic here
    # This is the placeholder — replace with DDG search / __NEXT_DATA__ parsing / etc.
    raise NotImplementedError(f"scrape_one not implemented for {url}")


if __name__ == "__main__":
    asyncio.run(main())
