# Рейтинг проектов для конвертации в Apify актор

## #1 — skool-scrape-signals → "Skool AI Lead Hunter"

Рейтинг: ДЕЛАТЬ

Уникальность: существующие акторы дают сырые данные, этот находит buying signals с AI.
Конкуренция: нулевая в нише AI lead finder (все конкуренты — просто scrapers).
Зрелость кода: продакшен, работает несколько месяцев на VPS.
Сложность конверсии: 1-2 дня.

Что нужно поменять:
- config.json + cookies_file → Actor.get_input() (cookies как поле INPUT)
- PostgreSQL дедупликация → KeyValueStore (set of processed IDs)
- Telegram нотификации → убрать (актор сам отдаёт Dataset)
- JSON файлы → Actor.push_data(record)
- Actor.charge("signal-found", 0.005) на каждый is_signal=True

Ограничение: требует Skool cookies и OpenRouter API key от пользователя — стандартная практика.

## #2 — email_verifier

Рейтинг: НЕ ДЕЛАТЬ (пока)

Причина: AWS/Apify блокирует порт 25. SMTP верификация — главная фишка — не работает.
Без SMTP это обычный DNS/MX чекер, который делают все конкуренты за $0.60/1000.
Конкурент michael.g: $0.60/1000, рейтинг 5.0, 134 MAU — убить нереально.

Когда имеет смысл: если найти способ роутить SMTP через residential proxy с открытым портом 25.

## #3 — tg-monitoring

Рейтинг: НЕ ДЕЛАТЬ

Причины:
- Telethon = persistent daemon, Apify акторы = run→finish (архитектурный конфликт)
- TG API авторизация требует интерактивного SMS-кода (невозможно в акторе)
- Все TG акторы работают только с публичными каналами — у нас нет преимущества
- Это personal tool завязанный на конкретные группы и сессию
