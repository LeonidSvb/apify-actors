# {{ACTOR_TITLE}}

{{ONE_LINE_DESCRIPTION}} — no login required, works out of the box.

---

## Quick Start

Paste this into the Input tab and click Run:

```json
{
  "startUrls": [{ "url": "https://www.skool.com/{{SAMPLE_COMMUNITY}}" }],
  "limit": 10
}
```

Results appear in the Dataset tab within seconds.

---

## What you get

Each result is a flat JSON object ready for spreadsheets, Zapier, Make, or AI pipelines:

```json
{
  "{{MAIN_FIELD_1}}": "{{EXAMPLE_VALUE_1}}",
  "{{MAIN_FIELD_2}}": "{{EXAMPLE_VALUE_2}}",
  "{{MAIN_FIELD_3}}": {{EXAMPLE_VALUE_3}},
  "created_at": "2026-01-15T10:30:00Z",
  "days_ago": 12,
  "_meta": {
    "actor": "{{ACTOR_SLUG}}",
    "version": "0.1.0",
    "scraped_at": "2026-06-04T09:00:00Z",
    "total_found": 47,
    "run_id": "abc123"
  }
}
```

Full list of fields: see [Input → Output tab](#) in the Actor console.

---

## Cost calculator

All prices include residential proxies. No hidden fees.

| What you scrape | Approx. cost |
|---|---|
| 10 results (try it) | ~$0.01 |
| 100 results | ~$0.05 |
| 500 results | ~$0.25 |
| 1,000 results | ~$0.50 |

On Apify's free plan ($5/month) you get approximately **1,000 results**.

---

## Input parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | — | Skool community URLs. **Required.** |
| `limit` | integer | 50 | Max results to return. Controls cost. |
| `requestTimeout` | integer | 30 | Seconds to wait per page (increase for slow connections). |
| `proxyConfiguration` | object | Residential | Proxy settings. Residential required for Skool. |

---

## How it works

{{HOW_IT_WORKS_3_4_LINES}}

---

## Limitations

- Only public Skool communities are supported. Private/members-only communities return an error.
- {{ADDITIONAL_LIMITATION_1}}
- {{ADDITIONAL_LIMITATION_2}}
- Rate limits: the actor adds a delay between requests to avoid blocks. Very large runs may take a few minutes.

---

## Use cases

1. **Lead generation** — {{USE_CASE_1}}
2. **Market research** — {{USE_CASE_2}}
3. **Competitor analysis** — {{USE_CASE_3}}
4. **Content monitoring** — {{USE_CASE_4}}
5. **AI/automation pipelines** — Feed results directly into Make, Zapier, or an LLM workflow.

---

## FAQ

**Q: Do I need a Skool account?**
A: {{COOKIES_ANSWER}}

**Q: Why am I getting 0 results?**
A: The community may be private, or Skool's WAF blocked the request. Make sure you are using residential proxies (default setting). If the issue persists, check the [Issues tab](issues) — Skool sometimes changes their page structure.

**Q: How fresh is the data?**
A: The actor scrapes in real time — data is as fresh as the moment you run it.

**Q: Can I run this on a schedule?**
A: Yes. In Apify Console, go to Schedules and set up a recurring run (daily, weekly, etc.).

**Q: {{ACTOR_SPECIFIC_FAQ_Q}}**
A: {{ACTOR_SPECIFIC_FAQ_A}}

---

## Related actors

- [Skool Community Finder](https://apify.com/{{YOUR_USERNAME}}/skool-community-finder) — discover communities by keyword
- [Skool Lookalike Finder](https://apify.com/{{YOUR_USERNAME}}/skool-lookalike-finder) — find similar communities to a given one
- [Skool Posts Scraper](https://apify.com/{{YOUR_USERNAME}}/skool-posts-scraper) — scrape posts, comments, and author contacts
- [Skool Community Profiler](https://apify.com/{{YOUR_USERNAME}}/skool-community-profiler) — activity stats, top members, admin detection

---

*Built by {{YOUR_NAME}}. Issues and feature requests welcome via the [Issues tab](issues).*
