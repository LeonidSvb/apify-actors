# Конкуренты в Apify Store — данные на июнь 2026

Источник: Apify Store API `GET /v2/store?search=skool&limit=50`
Точные позиции, не случайная выборка.

## Итого по запросу "skool": 179 акторов
Реально уникальных: ~30-35. Остальное — клоны одних и тех же акторов от разных аккаунтов
(api-empire, scrapier, simpleapi, scrapeflow, scrapebase, scrapapi — по 1-2 юзера каждый).

---

## Топ-8 по позиции в поиске (точные позиции)

| Поз | Актор | Total runs | Monthly | Stars | Reviews | Rating | Total users | 30d users | Цена |
|---|---|---|---|---|---|---|---|---|---|
| 1 | memo23/skool-posts-with-comments | 7,292 | 705 | 44 | 20 | 4.15 | 874 | 52 | $4.50/1k |
| 2 | gordian/skool-group-scraper | 713 | 136 | 3 | 1 | 5.0 | 146 | 30 | PPE |
| 3 | crustapi/skool-community-scraper | 426 | 315 | 0 | 0 | — | 82 | 36 | $3/1k |
| 4 | memo23/skool-members-scraper | 10,062 | 150 | 56 | 8 | 4.41 | 666 | 49 | PPE |
| 5 | goat255/skool-scraper-goat | 1,229 | 66 | 9 | 3 | 2.78 | 129 | 10 | $9/1k |
| 6 | easyapi/skool-groups-scraper | 446 | 15 | 4 | 1 | 5.0 | 57 | 6 | PPE |
| 7 | silentflow/skool-scraper-ppe | 250 | 59 | 2 | 0 | — | 30 | 10 | $3.50/1k |
| 8 | dz_omar/skool-scraper-pro | 1,166 | 404 | 19 | 4 | 5.0 | 335 | 52 | FREE |

## Скрытый игрок (вне топ-8)
cristiantala/skool-all-in-one-api: total 6,098 runs, monthly 3,394 (!), 71 users, 36 monthly users.
Программный/API паттерн использования — каждый юзер гоняет ~94 раза в месяц.

---

## Категории и насыщенность

| Категория | Кол-во акторов | Насыщенность |
|---|---|---|
| Group/Community info | ~40 (в основном клоны) | Перенасыщена |
| Members scraper | ~15 | Насыщена |
| Posts + comments | ~10 | Средняя |
| Classroom/video | ~5 | Низкая |
| Events | ~3 | Низкая |
| Profile scraper | ~8 | Средняя |
| AI lead finder / buying signals | 0 | ПУСТАЯ |
| Followers | ~6 | Средняя |

---

## SEO Apify Store — как работает ранжирование

На основе реальных данных позиций vs метрик:

1. Stars (звёзды) — главный фактор. dz_omar с 19 звёздами и лучшей monthly активностью стоит ниже
   gordian с 3 звёздами. Stars важнее monthly runs.

2. Историческое накопление users / runs — total users коррелирует с позицией.

3. Текстовое совпадение названия с запросом — "skool-group-scraper" прямо совпадает.

4. Monthly activity — вторичный буст (crustapi на #3 без звёзд за счёт 315 monthly runs).

5. FREE модель — даёт органический трафик но не буст в ранжировании.

Вывод: первые 15-20 отзывов со звёздами = критически важны для позиции.

---

## Email Verifier-ниша

| Актор | Цена/1000 | Рейтинг | MAU | SMTP? |
|---|---|---|---|---|
| michael.g/email-verifier-validator | $0.60 | 5.0 (7 отзывов) | 134 | Да |
| ryanclinton/bulk-email-verifier | $5.00 | — | — | Да |
| overpowered/verify-email | $1.00 | — | — | — |
| tomba-io/email-verifier | $1.01 | — | — | — |

КРИТИЧНО: AWS/Apify блокирует порт 25 outbound — SMTP верификация не работает на Apify.

## Telegram-ниша

| Актор | Цена/1000 | Рейтинг | MAU | Auth нужна? |
|---|---|---|---|---|
| tri_angle/telegram-scraper | $1.25 | 1.2 (14 отзывов) | 151 | Нет |
| ml_boost/tg-apify-actor | $3 + $0.0008/AI | 0.0 | 0 | Нет |

Все TG-акторы — только публичные каналы через веб. MTProto/Telethon невозможен.
