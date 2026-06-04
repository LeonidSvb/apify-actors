# Анализ жалоб: чему учат топовые акторы
Дата: 2026-06-04

---

## Полная карта Skool конкурентов (обновлено)

Нашли больше акторов чем было в TODO:

| Актор | Users | Rating | Reviews | Cookies? | Цена |
|---|---|---|---|---|---|
| memo23/skool-posts-with-comments | 875 | 4.0★ | 20 | Да | $4.50/1k |
| memo23/skool-members-scraper | 666 | 4.4★ | 8 | Да | $2.50/1k |
| dz_omar/skool-scraper-pro | 341 | 5.0★ | 6 | Опционально | PPE |
| crustapi/skool-community-scraper | 84 | — | 0 | Нет | $3.00/1k |
| silentflow/skool-scraper-ppe | 30 | — | 0 | Нет | $3.50/1k |
| silentflow/skool-scraper | 5 | — | 0 | Нет | $13.99/мес |

**crustapi/skool-community-scraper** — прямой конкурент Actor 1. Cookieless, 84 users, 45 data fields, автопагинация по 10 категориям Skool, доходит до #57,000+ комьюнити. Новый, 0 отзывов — ещё не раскрылся.

---

## 1. Почему куки убивают рейтинг

### Цикл смерти рейтинга (реальный паттерн)

```
День 1:   Пользователь ставит актор → работает → 5 звёзд в голове
День 45:  Cookie истекает/инвалидируется
День 45:  Актор падает с: "TooManyRedirects" или "Failed to authorize"
День 45:  Пользователь не понимает что происходит — думает актор сломан
День 45:  1-2 звезды: "stopped working", "broken", "waste of money"
```

Это НЕ баг разработчика. Это UX-провал: ошибка непонятная, нет инструкции что делать, нет превентивного предупреждения.

### Почему куки ломаются быстрее чем ожидает пользователь

Пользователь думает: "cookie живёт 1-3 месяца". Реальность:

| Причина | Когда происходит | Следствие |
|---|---|---|
| IP смена | Каждый ран Apify = новый IP | LinkedIn/Skool видят что cookie использован с другого IP → инвалидируют |
| Параллельные раны | Concurrent runs | Один cookie с разных IP одновременно → бан сессии |
| Platform security rotation | Без предупреждения | Всё работало вчера, сегодня нет |
| 2FA сессия | При любом suspicious activity | Требует повторную авторизацию |
| Cookie истёк по времени | 1-3 месяца | Ожидаемо, но пользователи забывают |

**Итог:** пользователь обновляет cookie → ещё раз инвалидируется от нового IP → обновляет третий раз → всё ещё не работает → 1 звезда.

Реальная жалоба найдена на Apify: *"added new cookies for the third time and still doesn't work"*.

### Почему это убивает именно рейтинг (а не просто создаёт тикеты)

1. Пользователь заплатил → не работает → злится
2. Пользователь не знает что это временная проблема решаемая за 2 минуты
3. Ставит 1 звезду до того как пишет в support
4. Разработчик отвечает, проблема решается — но отзыв уже не меняется

У curious_coder/linkedin-profile-scraper 2.7★ именно из-за этого цикла. У curious_coder/linkedin-post-scraper 3.2★ (18 reviews) — та же история.

---

## 2. Топ-10 жалоб по всем акторам (паттерны)

### #1 — Пустой output без объяснений (самая частая)

**Пример:** Instagram scraper issue "Empty or private data for provided input"

Пользователь запускает, получает 0 результатов, не понимает почему:
- Приватный аккаунт? Заблокирован IP? Неправильный URL? Актор сломан?
- Пишет 1-звёздный отзыв "does not work"

**Предотвращение:**
- Явная проверка в начале: приватный/публичный ресурс, валидный URL
- `Actor.fail()` с конкретным сообщением: "Community appears to be private. Only public communities are supported."
- `Actor.set_status_message()` во время работы чтобы показать прогресс
- Никогда не завершать с 0 результатами молча

---

### #2 — Куки/сессия истекли (второй по частоте)

**Реальные жалобы:**
- "TooManyRedirects errors because the cookie has been invalidated"
- "added new cookies for the third time and still doesn't work"
- "Failed to authorize with linkedin. Please retry with new cookies"

**Предотвращение:**
- Валидация cookie В САМОМ НАЧАЛЕ до любой работы
- Конкретная ошибка: "Your Skool session has expired. Please export fresh cookies. See README > Cookie Setup for step-by-step instructions."
- `Actor.fail()` немедленно при невалидных куках, не тратить $$ впустую
- В README: пошаговая инструкция обновления с скриншотами
- В README: секция "Cookie FAQ" — как долго живёт, почему истекает, как обновить

---

### #3 — WAF/прокси блокировки (Skool-специфично)

**Реальные данные:** Skool использует AWS WAF. Datacenter прокси → blocked.

Пользователи получают 0 results или 403 без понимания почему:
- "not using residential proxies will get partial results like a free user"
- Юзеры запускают с дефолтными прокси → ничего не приходит

**Предотвращение:**
- Residential proxies как дефолт в INPUT_SCHEMA (не опция)
- В README заглавными: "Skool requires residential proxies. Datacenter proxies return empty results."
- `Actor.set_status_message("Detected potential proxy block. Retrying with residential proxy...")`
- Structured error: `{ "error": "proxy_blocked", "message": "...", "retry": true }`

---

### #4 — Email scraping не работает как ожидается

**Реальные issues (Skool):**
- "Scraper not pulling emails" 
- "Not scraping email addresses"
- Поддержка: "emails only visible to group admins"

Пользователи ожидают email у каждого члена, получают null у большинства → злятся.

**Предотвращение:**
- В README явно: "Emails are only visible when the member has made them public OR you are an admin of the community"
- Output: всегда включать поле `email: null` (не пропускать поле совсем)
- Добавить поле `email_available: true/false` чтобы пользователь понимал масштаб
- Документировать: "average email extraction rate is ~15-20% of members"

---

### #5 — Актор сломался после обновления платформы

**Реальный пример:** Website Content Crawler сломался после версии 0.3.36.

Skool-специфично: `__NEXT_DATA__` структура может поменяться в любой момент.

**Предотвращение:**
- Changelog обязателен в actor.json/README
- Structured error для schema changes: `{ "error": "schema_changed", "message": "Skool updated their page structure. We are working on a fix.", "retry": false }`
- Мониторинг: health check ран каждые 24ч, если 0 results → alert
- В README: "If the actor returns 0 results unexpectedly, check the Changelog and Issues tabs first"

---

### #6 — Актор не обновляется / мёртвый разработчик

**Примеры:** curious_coder/instant-web-scraper — 4.9★ но не обновлялся 2 года.

Пользователи не понимают что актор работает но не поддерживается. Когда Skool меняет структуру — актор ломается, никто не чинит.

**Предотвращение:**
- GitHub Actions auto-deploy из main
- Дата последнего обновления всегда видна — держать свежей
- Версионирование по semver: 1.0.0 → 1.0.1 при фиксах
- "Maintenance status" badge в README

---

### #7 — Запутанный или неполный input

**Пример:** Пользователь не знает какой URL передавать, какой формат, что обязательно.

**Реальные жалобы:**
- Неправильный формат URL → актор молча завершается
- Не ясно что параметр обязательный
- Дефолтный input не работает

**Предотвращение:**
- Все параметры с description и example в INPUT_SCHEMA
- `prefill` значения которые реально работают без изменений
- Input validation с понятными ошибками: "communityUrls must be an array of Skool URLs like ['https://www.skool.com/community-name']"
- "Try with defaults" должен реально работать — тестировать при каждом деплое

---

### #8 — Цена неожиданно высокая

**Реальная жалоба (найдена в поиске):** "while actors offer affordable pricing initially, these costs often do not cover additional charges for proxies"

Пользователь видит $0.005/community → радуется → получает счёт за residential proxies которые в 3x дороже.

**Предотвращение:**
- Cost calculator в README: "Scraping 100 communities with residential proxies costs approximately $X total"
- Явно указать что residential proxies входят в цену (или нет)
- PPE должен включать стоимость прокси — не скрывать

---

### #9 — Rate limiting → бан аккаунта

**Пример:** LinkedIn Profile Scraper предупреждает "don't scrape more than 500 profiles per day".

Пользователи игнорируют лимиты → аккаунт блокируется → 1 звезда.

**Предотвращение:**
- Жёсткий enforceable лимит в коде, не только в README
- `requestDelay` как обязательный параметр с разумным дефолтом
- Предупреждение при старте: "Running at 0.35s delay to avoid rate limiting"
- Документировать: "What happens if you ignore rate limits"

---

### #10 — Приватное комьюнити / нет доступа

**Skool-специфично:** Некоторые комьюнити закрытые, требуют апрув.

Пользователь передаёт URL закрытого комьюнити → 0 results → думает актор сломан.

**Предотвращение:**
- Детектировать "private/closed community" в начале
- Структурированный error: `{ "error": "private_community", "community": "...", "message": "This community requires membership to access. Only public communities are supported." }`
- В output включать поле `is_public: false` для таких комьюнити
- В README: список того что НЕ поддерживается

---

## 3. Специфика наших акторов с куками

По плану с куками: Actor 2 (Lookalike), Actor 3 (Posts Scraper), Actor 4 (Profiler).

### Как работать с куками чтобы не убить рейтинг

**Стратегия "Fail Fast, Explain Everything":**

```python
# 1. Валидируем cookie ДО любой работы
Actor.set_status_message("Validating session...")
if not await validate_skool_session(cookies):
    await Actor.fail(
        status_message=(
            "Session cookie is invalid or expired. "
            "Please export fresh cookies from your browser. "
            "See README > Cookie Setup for step-by-step instructions."
        )
    )
    return
```

**Обязательные секции в README для cookie-акторов:**

1. "Cookie Setup" — пошагово с скриншотами, до 5 шагов
2. "Cookie FAQ":
   - "How long do cookies last?" — 1-3 месяца, но может быть меньше
   - "Why did my cookie stop working?" — IP change объяснить
   - "I updated my cookie but it still fails" — parallel runs, clear solution
3. "When to refresh your cookie" — признаки что пора обновить
4. Error messages guide: что каждая ошибка означает и что делать

**Ключевой принцип:** пользователь должен понять что делать из сообщения об ошибке, не заходя в support.

---

## 4. Как избежать "актор сломался после обновления Skool"

Skool меняет `__NEXT_DATA__` структуру без предупреждения. Это самый непредсказуемый риск.

**Защитная архитектура:**

```python
# Graceful degradation: всегда возвращай что-то, объясняй что пропущено
try:
    post_data = parse_next_data(raw_html)
except SchemaChangedError:
    Actor.log.warning("Skool page structure changed. Some fields may be missing.")
    post_data = parse_next_data_fallback(raw_html)  # базовые поля
    post_data["_parse_warning"] = "partial_data_schema_changed"
```

**Мониторинг:**
- Health check ран: простой ран на известное публичное комьюнити
- Если структура изменилась → `_meta.schema_version` меняется → алерт
- GitHub Actions: daily health check, если fails → Issue автосоздаётся

---

## 5. Выводы и план действий

### Что защищает от плохих отзывов

| Действие | Ценность | Сложность |
|---|---|---|
| `Actor.fail()` с понятным сообщением | Убирает 40% 1-звёздных отзывов | Низкая |
| Cookie validation на старте | Убирает "added cookie 3 times" жалобы | Низкая |
| Residential proxy как дефолт | Убирает WAF/0 results жалобы | Низкая |
| Cookie FAQ в README | Пользователь решает сам без support | Низкая |
| Явные лимиты в коде | Предотвращает аккаунт баны | Средняя |
| Health check мониторинг | Ловит Skool changes быстро | Средняя |
| Cost calculator в README | Убирает "цена неожиданно высокая" | Низкая |
| Input validation | Убирает молчаливые провалы | Низкая |

### На что ориентируемся у конкурентов

- **memo23** — опытный в Skool, знает edge cases, медленно реагирует на схема-изменения
- **silentflow/skool-scraper-ppe** — прямой конкурент Actor 3, cookieless, 30 users, новый — следить
- **crustapi** — прямой конкурент Actor 1, cookieless, автодискавери — следить
- **dz_omar** — classroom-специализация, не прямой конкурент

### Наше незанятое пространство

Никто из конкурентов не делает:
- Lookalike finder через overlap analysis
- AI-first flat JSON с computed fields
- `_meta` блок
- Cost calculator в README
- Явные cookie FAQ секции
- Structured errors с `retry: bool`
- Actor.fail() вместо пустого датасета
