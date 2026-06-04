# Стратегия публикации акторов

Обновлено: 2026-06-04

## Финальная архитектура (без LLM на старте)

4 атомарных актора. LLM — опциональная фича, добавим позже когда наберут аудиторию.

| # | Актор | Cookies | LLM | Уникальность | Приоритет |
|---|---|---|---|---|---|
| 1 | Community Finder | НЕТ | НЕТ | Средняя | 1й — максимум аудитории |
| 2 | Lookalike Finder | ДА | НЕТ | МАКСИМАЛЬНАЯ | 2й — нет нигде |
| 3 | Posts + Contacts | ДА | НЕТ | Средняя | 3й — конкурентная ниша |
| 4 | Community Profiler | ДА | НЕТ | Высокая | 4й |

## Почему убрали ICP segmentation и keyword scoring

ICP сегментация в исходнике — чистый keyword matching, не LLM. Проблема:
- Захардкожена под нашу нишу (System Hustle / agency owners)
- Давала шум — нужен был LLM чтобы реально отфильтровать
- Чужие пользователи ищут другой ICP

Решение: отдаём raw data в удобном формате, пользователь сам обогащает под свой юзкейс.
Объективные метрики (member_count, activity_ratio, access, price_usd) одинаково полезны всем.

## LLM — план на потом

Когда первые акторы наберут аудиторию и reviews:
- Добавить опциональный параметр `openrouterKey` в каждый актор
- Добавить опциональный параметр `icpDescription` (пользователь описывает свой ICP)
- Актор классифицирует результаты если ключ предоставлен, иначе отдаёт сырые данные
- PPE event за AI enrichment отдельно от базового события

## Ключевые данные по конкурентам (июнь 2026)

Запрос "skool" в Apify Store: 179 акторов, из них реально уникальных ~30-35.

Топ конкуренты:
- memo23/skool-posts-with-comments: #1, 7,292 runs, 874 users, 44 stars, $4.50/1k
- memo23/skool-members-scraper: #4, 10,062 runs, 56 stars (больше всех)
- dz_omar/skool-scraper-pro: FREE, 335 users, 5.0 rating — много юзеров через FREE

Наши акторы vs конкуренты:
- Actor 1: нет прямого конкурента с ICP-нейтральным discovery + ranking
- Actor 2: Lookalike — нет нигде
- Actor 3: конкурирует с memo23, дифференциатор = dedup + contacts в данных
- Actor 4: нет прямого конкурента

## SEO ранжирование в Store

На основе реальных данных позиций:
1. Stars (звёзды) — главный фактор
2. Historical users/runs — накопленный вес
3. Текстовое совпадение названия с запросом
4. Monthly activity — вторичный буст
Первые 15-20 отзывов = критично для позиции. Собирать только органически.

## Политика free tier

Free tier ($5/мес) НЕ генерирует revenue для разработчика.
"Payout invoices only include funds from legitimate users who have already paid."
Review abuse = ретроактивный возврат всех выплат.

## Deduplication across runs — реализация

```python
store = await Actor.open_key_value_store(name="skool-posts-dedup-{slug}")
processed = set(await store.get_value("post_ids") or [])
# ... process only new posts ...
await store.set_value("post_ids", list(processed))
```

10-15 строк. Scales до тысяч ID без проблем.

## AI-first дизайн (для API/агентского использования)

- Плоский JSON, не более 2 уровней вложенности
- Все поля всегда в output (null вместо отсутствия)
- Computed fields рядом с raw (days_ago + created_at)
- Structured errors с полем retry: bool
- _meta блок в каждом output
- limit параметр обязателен
- Детерминированный порядок результатов
- Actor.fail() при 0 результатах (сохраняет видимость в Store)
