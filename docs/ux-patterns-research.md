# UX Research: Топ Акторы Apify Store
Дата: 2026-06-04

---

## Акторы в исследовании

| Актор | Разработчик | Пользователи | Рейтинг | Отзывы | Цена |
|---|---|---|---|---|---|
| Google Maps Scraper | compass | **438K** | 4.8★ | 1434 | от $1.50/1000 |
| Instagram Scraper | apify | **285K** | 4.7★ | 439 | $1.50/1000 |
| LinkedIn Jobs Scraper | curious_coder | **92K** | 4.4★ | 98 | $1.00/1000 |
| Facebook Ad Library | curious_coder | **28K** | 4.7★ | 93 | $0.75/1000 |
| LinkedIn Sales Navigator | curious_coder | 8K | 4.5★ | 35 | $39/мес |
| LinkedIn Profile Scraper | curious_coder | 5.7K | 2.7★ | 13 | $4.00/1000 |
| LinkedIn People Search | curious_coder | 2.3K | 4.2★ | 10 | $20/мес |
| Facebook Marketplace | curious_coder | 3.9K | 2.8★ | 4 | PPE |
| Instant Web Scraper | curious_coder | 2K | 4.9★ | 4 | $10/мес |
| Skool Posts Scraper | memo23 | 875 | 4.0★ | 20 | $4.50/1000 |

---

## 1. Что делают лучшие акторы правильно

### compass/google-maps (438K, 4.8★) — золотой стандарт

**Почему у него 438K пользователей:**
- Ломает лимит Google Maps API (120 мест) — решает боль которую нельзя решить официально
- Гибкий input: текст + локация + категории + GeoJSON + прямые URL — каждый пользователь находит свой путь
- Pay-as-you-go от $1.50/1000 — низкий барьер входа
- Webhook + MCP server совместимость — попадает в AI workflow тренд
- Три режима просмотра: таблица, JSON, карта — разные типы пользователей
- 1434 отзывов = социальное доказательство которое само продаёт

**Ключевые паттерны:**
- Каждый input параметр делает одно простое дело
- Нет обязательных параметров кроме одного (search term или URL)
- Enrichment add-ons как опциональные надстройки — базовый юз-кейс дешевле

### apify/instagram-scraper (285K, 4.7★) — стандарт README

**README структура которую стоит копировать:**
1. Одна строка — что делает
2. Feature list с эмодзи — быстрое сканирование (только они просили эмодзи — для нас без)
3. **Cost calculator** — "на $29/мес получаешь 12,600 results" — уникальная фича, нигде больше нет
4. Sample JSON output — полный реальный пример
5. Legal/GDPR секция — доверие
6. Related actors карусель — cross-promotion
7. API docs

**Ключевые паттерны:**
- `searchType` enum (place | hashtag | profile) — один параметр управляет поведением
- `resultsLimit` — пользователь контролирует расходы
- Цена разбита по типам: посты $1.50/1000, комментарии $2.30/1000 — прозрачно

### curious_coder/linkedin-jobs (92K, 4.4★) — лучший у curious_coder

**Почему работает:**
- Решает специфический limitation LinkedIn (лимит 1000 jobs) через location splitting — это killer feature
- Cookieless — нулевой барьер входа
- Раздел "How to scrape new jobs every day automatically" — обучает пользователя правильному использованию
- PPR $1.00/1000 — просто и понятно

**Ключевые паттерны:**
- README секции под конкретные задачи (не "features", а "how to scrape more than 1000")
- Sample output с реальными полями
- Scheduling guide включён в README

---

## 2. Что у curious_coder хорошо

- **98.3% success rate** на 36 акторах — техническая надёжность
- **42K monthly active users** — реальный продакшн трафик
- Всегда есть sample output в README
- PPE/PPR модели у большинства — no upfront cost
- Специализация на LinkedIn = высокоценные данные для B2B

---

## 3. Что не очень у curious_coder

| Проблема | Пример | Эффект |
|---|---|---|
| Cookie-зависимые акторы | LinkedIn Profile (2.7★), People Search | Высокий барьер входа → низкий рейтинг |
| Месячная подписка | Sales Navigator $39/мес, People Search $20/мес | Психологический барьер — пользователи не пробуют |
| Непоследовательный README | У каждого актора своя структура | Нет узнаваемого бренда |
| Нет cost calculator | Никто у curious_coder не делает | Instagram scraper сразу выигрывает доверие |
| Нет status messages | Актор просто работает молча | Пользователь не знает жив ли ран |
| Нет related actors секции | Каждый актор изолирован | Упущенный cross-promotion |
| Устаревшие акторы | Instant Web Scraper не обновлялся 2 года | Рейтинг 4.9 но 2K юзеров — недооткрыт |

---

## 4. memo23/skool-posts — наш прямой конкурент

- 875 пользователей, 4.0★, 20 отзывов — **очень мало для ниши**
- Требует cookies — высокий барьер
- Нет computed fields (days_ago, activity_ratio)
- Нет _meta блока
- Нет structured errors
- README базовый, нет use cases, нет cost guide

**Вывод:** ниша Skool скраперов почти пустая. 875 пользователей = возможность.

---

## 5. Паттерны которые стоит взять как стандарт

### Input Schema (брать у compass + instagram)
```
keywords / searchQuery  — string, обязательный, с примером в title
limit / maxItems        — integer, default 50, max 500
requestTimeout          — integer, default 30
proxy                   — ProxyConfiguration object
startUrls               — array[string] (если URL-based)
```

### README структура (гибрид compass + instagram + curious_coder jobs)
1. **Шапка** — одна строка что делает + метрики (users, rating) как badges
2. **Quick Start** — минимальный рабочий input, копипаст
3. **What you get** — таблица полей output с типами и описанием
4. **Cost calculator** — "при $5 кредитов получишь ~X записей" (взять у instagram)
5. **How it works** — 3-4 строки технически
6. **Input parameters** — таблица: параметр | тип | дефолт | описание
7. **Limitations** — честно: закрытые комьюнити, rate limits
8. **Use cases** — 3-5 конкретных сценариев
9. **FAQ** — 3-5 вопросов
10. **Related actors** — ссылки на свои акторы

### Output паттерн (улучшаем compass + curious_coder)
- Flat JSON не глубже 2 уровней
- Computed fields рядом с raw: `days_ago` + `created_at`, `activity_ratio` + raw числа
- Все поля всегда присутствуют (null вместо отсутствия)
- `_meta` блок: `{ actor, version, scraped_at, total_found, run_id }`
- Structured errors: `{ error, message, retry: bool }`

### Ценообразование (PPE как у compass/instagram)
- Никаких месячных подписок — самый высокий конверсионный барьер
- PPE: Start fee + per-item fee — пользователь видит что платит за результат
- В README: cost calculator с конкретными числами

---

## 6. Где есть пространство роста

| Область | Что сейчас | Что можно сделать |
|---|---|---|
| Status messages | Почти никто не делает | `Actor.set_status_message()` — юзер видит прогресс |
| AI-first output | Вложенные JSON у всех | Flat + computed + _meta = идеальный input для LLM агентов |
| Actor.fail() при 0 | Никто не делает | Агент получает ошибку а не пустой датасет |
| Health check | Нет | 0 результатов = fail = сохраняет позицию в Store |
| MCP совместимость | Только compass делает | Указать в README что работает с Claude MCP |
| Dedup через KV Store | Никто из Skool акторов | "never pay twice for the same post" — killer feature |
| Skool ниша | 1 актор (875 юзеров) | 4 актора = монополия ниши |

---

## Вывод

**Брать как образец:** compass (архитектура + UX), apify/instagram (README + cost calculator), curious_coder/linkedin-jobs (решение ограничений платформы).

**Не зазнаваться:** наши акторы технически делают похожие вещи что и топы в других нишах. Разница не в коде — в документации, cost calculator, AI-first output и cross-promotion.

**Наше преимущество:** Skool ниша почти пустая. memo23 с 875 юзерами и базовым README — не конкурент если сделать правильно.
