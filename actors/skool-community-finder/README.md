# Skool Community Finder

Search and discover Skool communities by keyword — no login or cookies required.

---

## Quick Start

Paste this into the Input tab and click **Run**:

```json
{
  "keywords": ["cold email", "agency growth"],
  "limit": 20
}
```

Results appear in the **Dataset** tab within 1–2 minutes.

---

## What you get

Each result is a flat JSON object with all fields always present:

```json
{
  "slug": "cold-email-community",
  "url": "https://www.skool.com/cold-email-community",
  "group_id": "abc123",
  "name": "Cold Email Community",
  "description": "The #1 community for cold email practitioners...",
  "member_count": 15234,
  "online_members": 142,
  "access": "free_open",
  "price_usd": 0.0,
  "has_survey": false,
  "total_posts": 4821,
  "num_courses": 3,
  "activity_ratio": 0.3164,
  "last_post_date": "2026-06-03",
  "days_since_last_post": 1,
  "source": "ddg:cold email",
  "_meta": {
    "actor": "skool-community-finder",
    "version": "0.1.0",
    "scraped_at": "2026-06-04T09:00:00+00:00",
    "total_found": 47,
    "run_id": "xyz789"
  }
}
```

**Field reference:**

| Field | Description |
|---|---|
| `slug` | Community URL slug (unique identifier) |
| `url` | Direct link to the community |
| `name` | Display name |
| `description` | Community description (up to 400 chars) |
| `member_count` | Total member count |
| `online_members` | Members currently online |
| `access` | `free_open`, `free_survey`, `paid`, `invite_only`, or `public` |
| `price_usd` | Monthly price in USD (0 = free) |
| `has_survey` | Whether joining requires a questionnaire |
| `total_posts` | All-time post count |
| `num_courses` | Number of classroom courses |
| `activity_ratio` | `total_posts / member_count` — higher = more active per member |
| `last_post_date` | Date of most recent visible post (null if community is private) |
| `days_since_last_post` | Days since last post (null if not visible) |
| `source` | How the community was discovered (ddg:keyword or suggested) |

---

## Cost calculator

Pricing is **pay-per-result** — you only pay for what you get.

| Results | Approximate cost |
|---|---|
| 10 (try it) | ~$0.05 |
| 50 (default) | ~$0.25 |
| 100 | ~$0.50 |
| 200 (max) | ~$1.00 |

On Apify's **free plan** ($5/month credit) you get approximately **1,000 communities**.

Note: residential proxy traffic is included in the above estimates.

---

## Input parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `keywords` | string[] | — | Search terms. Each runs a separate DuckDuckGo search. **Required.** |
| `limit` | integer | 50 | Max communities to return (1–200). Controls cost. |
| `minMembers` | integer | 0 | Skip communities with fewer members. |
| `requestTimeout` | integer | 30 | Seconds per page (increase for slow connections). |
| `proxyConfiguration` | object | Residential | Proxy settings. Residential required for Skool. |

---

## How it works

1. **Keyword search** — runs `site:skool.com <keyword>` on DuckDuckGo and extracts community slugs from results
2. **Community probe** — fetches each community page and parses the `__NEXT_DATA__` JSON embedded in the HTML (no browser needed)
3. **Suggested harvest** — collects additional communities from each page's `suggestedCommunities` list, then probes those too
4. Results are streamed to the Dataset as they are found — you can see them before the run completes

No authentication required. All data comes from publicly accessible community pages.

---

## Limitations

- **Public communities only.** Private and invite-only communities are detected and skipped with a clear `access: "invite_only"` label.
- `days_since_last_post` is null for communities where the post feed is not publicly visible.
- DuckDuckGo occasionally rate-limits searches. If all keywords return 0 slugs, the actor fails with a clear message — try again in a few minutes.
- Member count and post count reflect what Skool shows on the public page, which may lag behind real-time data by a few hours.

---

## Use cases

1. **Lead generation** — find active communities in your niche and reach out to members or admins
2. **Market research** — survey the Skool landscape before launching your own community
3. **Competitor analysis** — monitor competitor community growth and activity over time (run on a schedule)
4. **Partnership prospecting** — identify large free communities for cross-promotion opportunities
5. **AI pipeline input** — feed results into Make/Zapier or an LLM agent for automated outreach or analysis

---

## FAQ

**Do I need a Skool account or cookies?**
No. This actor scrapes publicly accessible community pages without any login.

**Why am I getting 0 results?**
DuckDuckGo may be temporarily blocking the search. Wait 2–3 minutes and try again. Also try broader keywords like "online course" or "community". If the issue persists, check the Issues tab.

**How fresh is the data?**
Data is scraped in real time — as fresh as the moment you run it.

**Can I run this automatically every week?**
Yes. In Apify Console → Schedules, set up a recurring run with your keywords. Results accumulate in the Dataset across runs.

**What does `activity_ratio` mean?**
It's `total_posts / member_count`. A ratio of 0.3 means members have posted on average 0.3 times each. Higher values indicate more active communities.

---

## Related actors

- [Skool Lookalike Finder](#) — given a community, find other communities with overlapping members
- [Skool Posts Scraper](#) — scrape posts, comments, and author LinkedIn/social contacts
- [Skool Community Profiler](#) — deep activity stats, top posters, admin detection
