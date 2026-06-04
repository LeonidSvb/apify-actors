# Спецификации акторов

Исходный код: `C:\Users\79818\Desktop\tests\SCRAPING-LEADGEN\skool-scrape-signals\`

---

## Actor 1: Skool Community Finder

**Папка:** `actors/skool-community-finder/`
**Исходник:** `scripts/search_communities.py`
**Cookies нужны:** НЕТ
**LLM нужен:** НЕТ

### INPUT_SCHEMA

```json
{
  "keywords":    { "type": "string",  "required": true,  "example": "cold email outreach agency" },
  "limit":       { "type": "integer", "default": 50,     "max": 200 },
  "minMembers":  { "type": "integer", "default": 0 },
  "accessTypes": { "type": "array",   "default": ["free_open","free_survey","paid","public"],
                   "description": "Filter by access type" }
}
```

### OUTPUT (один record = одно комьюнити)

```json
{
  "slug":                "cold-email-community",
  "name":                "Cold Email Community",
  "url":                 "https://skool.com/cold-email-community",
  "description":         "...",
  "member_count":        12400,
  "online_members":      234,
  "access":              "free_open",
  "price_usd":           0,
  "has_survey":          false,
  "num_courses":         3,
  "total_posts":         8900,
  "activity_ratio":      0.71,
  "days_since_last_post": 0,
  "scraped_at":          "2026-06-04T10:30:00Z",
  "_meta": {
    "actor": "skool-community-finder",
    "source": "ddg_search | suggested | seed"
  }
}
```

### Что убрано vs исходника
- ICP segmentation (A/B/C) — субъективно, захардкожено под нашу нишу
- Keyword scoring — то же самое
- Seed slugs — не нужны в публичном акторе

### Pricing
PPE: Actor Start $0.005 + $0.003 per community found

### SEO
- seoTitle: "Skool Community Finder - Search & Discover Groups by Keywords"
- Категории: Lead Generation, Social Media

---

## Actor 2: Skool Lookalike Community Finder

**Папка:** `actors/skool-lookalike-finder/`
**Исходник:** `scripts/search_communities.py` (строки 487-521, cross-community discovery)
**Cookies нужны:** ДА
**LLM нужен:** НЕТ

### INPUT_SCHEMA

```json
{
  "communityUrls": { "type": "array",   "required": true,  "maxItems": 3,
                     "example": ["https://skool.com/cold-email-community"] },
  "cookies":       { "type": "array",   "required": true,  "isSecret": true },
  "topPostersN":   { "type": "integer", "default": 30, "description": "How many top posters to analyze per source community" },
  "limit":         { "type": "integer", "default": 50 },
  "minOverlapPct": { "type": "number",  "default": 0 }
}
```

### OUTPUT (один record = одно найденное комьюнити)

```json
{
  "slug":            "outreach-agency-owners",
  "name":            "Outreach Agency Owners",
  "url":             "https://skool.com/outreach-agency-owners",
  "overlap_count":   7,
  "overlap_pct":     35.0,
  "shared_posters": [
    { "name": "John Smith", "id": "abc123", "post_count": 45 }
  ],
  "member_count":    3200,
  "online_members":  89,
  "access":          "paid",
  "price_usd":       49,
  "has_survey":      false,
  "num_courses":     5,
  "total_posts":     4100,
  "activity_ratio":  0.54,
  "days_since_last_post": 1,
  "scraped_at":      "2026-06-04T10:30:00Z"
}
```

### Логика
1. Scrape top N posters из каждого source community
2. Для каждого poster: GET api2.skool.com/users/{uid}/groups
3. Подсчитать overlap_count (сколько source posters состоят в каждом найденном комьюнити)
4. Probe каждое найденное комьюнити (name, members, price, etc.)
5. Сортировка по overlap_pct DESC
6. Исключить source communities из результата

### Pricing
PPE: Actor Start $0.005 + $0.005 per community found

### SEO
- seoTitle: "Skool Lookalike Community Finder - Find Similar Groups"

---

## Actor 3: Skool Posts & Contacts Scraper

**Папка:** `actors/skool-posts-scraper/`
**Исходник:** `pipeline/scraper.py`
**Cookies нужны:** ДА
**LLM нужен:** НЕТ

### INPUT_SCHEMA

```json
{
  "communityUrls":        { "type": "array",   "required": true },
  "cookies":              { "type": "array",   "required": true, "isSecret": true },
  "hoursBack":            { "type": "integer", "default": 24, "description": "How far back to scrape" },
  "maxPostsPerCommunity": { "type": "integer", "default": 100 },
  "includeComments":      { "type": "boolean", "default": false },
  "minCommentsForFetch":  { "type": "integer", "default": 1, "description": "Fetch comments only for posts with >= N comments" },
  "dedup":                { "type": "boolean", "default": true, "description": "Skip posts seen in previous runs" }
}
```

### OUTPUT (один record = один пост)

```json
{
  "id":             "post_abc123",
  "community":      "cold-email-community",
  "category":       "Questions",
  "title":          "Looking for cold email tool",
  "content":        "...",
  "url":            "https://skool.com/cold-email-community/looking-for-cold-email-tool",
  "upvotes":        12,
  "comments_count": 8,
  "created_at":     "2026-06-03T14:22:00Z",
  "days_ago":       1,
  "author": {
    "name":     "John Smith",
    "id":       "abc123",
    "linkedin": "https://linkedin.com/in/johnsmith",
    "website":  "https://johnsmith.com",
    "bio":      "Agency owner..."
  },
  "comments": [
    {
      "id":         "comment_xyz",
      "content":    "...",
      "created_at": "2026-06-03T15:00:00Z",
      "upvotes":    3,
      "author": {
        "name":     "Jane Doe",
        "id":       "def456",
        "linkedin": null,
        "website":  null
      },
      "replies": []
    }
  ]
}
```

### Dedup
KV Store name: `"skool-posts-dedup-{community_slug}"`
Хранит set обработанных post_id. Persists between runs.

### Pricing
PPE: Actor Start $0.005 + $0.003 per post

### SEO
- seoTitle: "Skool Posts Scraper - Posts, Comments & Author LinkedIn Contacts"
- Ключевое в README: dedup across runs = не платишь дважды за один пост

---

## Actor 4: Skool Community Profiler

**Папка:** `actors/skool-community-profiler/`
**Исходник:** `scripts/explore_communities.py`
**Cookies нужны:** ДА
**LLM нужен:** НЕТ

### INPUT_SCHEMA

```json
{
  "communityUrls": { "type": "array",   "required": true },
  "cookies":       { "type": "array",   "required": true, "isSecret": true },
  "postsToScan":   { "type": "integer", "default": 100, "max": 500 }
}
```

### OUTPUT (один record = одно комьюнити)

```json
{
  "slug":             "cold-email-community",
  "name":             "Cold Email Community",
  "url":              "https://skool.com/cold-email-community",
  "member_count":     12400,
  "posts_scanned":    100,
  "scan_period_days": 14,
  "oldest_post":      "2026-05-20",
  "newest_post":      "2026-06-03",
  "posts_per_day":    7.1,
  "activity_ratio":   0.71,
  "categories": {
    "Questions": 45,
    "Wins": 22,
    "General": 33
  },
  "top_posters": [
    {
      "name":         "John Smith",
      "id":           "abc123",
      "post_count":   12,
      "pct":          12.0,
      "likely_admin": true,
      "linkedin":     "https://linkedin.com/in/johnsmith"
    }
  ],
  "likely_admins": ["abc123", "def456"],
  "scraped_at":    "2026-06-04T10:30:00Z"
}
```

### Логика likely_admin
Автор у которого >= 8% от всех отсканированных постов = likely_admin.
Это эвристика, не гарантия.

### Pricing
PPE: Actor Start $0.005 + $0.005 per community profiled

### SEO
- seoTitle: "Skool Community Profiler - Activity Stats, Top Members & Admins"

---

## Общие принципы для всех акторов

### AI-first дизайн
- Плоский JSON (не более 2 уровней вложенности в ключевых полях)
- Все поля всегда присутствуют (null вместо отсутствия)
- Computed fields рядом с raw (days_ago рядом с created_at)
- Structured errors: { "error": "code", "message": "...", "retry": bool }
- _meta блок с actor, version, scraped_at, total_found
- Детерминированный порядок (всегда один и тот же sort)
- limit параметр обязателен

### Structured errors (стандарт)
```json
{ "error": "invalid_cookies",    "message": "Cookies expired — refresh from browser", "retry": false }
{ "error": "community_private",  "message": "Community requires membership",           "retry": false }
{ "error": "rate_limited",       "message": "Skool rate limit hit, retry in 60s",      "retry": true  }
{ "error": "no_results",         "message": "No communities found for keywords",        "retry": false }
```

### Actor.fail() триггеры
- 0 результатов при непустом input
- Cookies невалидны (HTTP 401/403)
- __NEXT_DATA__ структура изменилась (нет ожидаемых полей)
