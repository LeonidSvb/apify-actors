# Подводные камни Apify акторов

Источник: анализ 54 билдов + статья "99% of scrapers get zero users"

## Технические (убивают до запуска)

### 1. Build system важнее scraping logic
"The scraper logic was NOT the main thing breaking. The build system was."
- Не менять Dockerfile и schema paths одновременно
- После каждого рефакторинга — изолировать изменения по одной системной границе
- Типичный фейл: путь INPUT_SCHEMA съехал с `"./INPUT_SCHEMA.json"` на `"../INPUT_SCHEMA.json"` → билд падает

### 2. Docker permissions — exit code 243
```dockerfile
# Неправильно
COPY . .

# Правильно
COPY --chown=myuser:myuser . .
```

### 3. "Click Run with defaults" ДОЛЖЕН работать
Тестировать на чистом аккаунте, не на dev-окружении. Большинство пользователей не читают доку.

### 4. Silent failures
Актор завершается exit 0, датасет пустой — Apify не видит ошибки, пользователь уходит.
```python
results = scrape(...)
if not results:
    await Actor.fail("No data returned — Skool may have changed structure")
```

### 5. Port 25 заблокирован
AWS/Apify блокирует исходящий порт 25. SMTP верификация email — невозможна. С 2020 года без исключений.

## Продуктовые (убивают после запуска)

### 6. SEO в Store — критично
Store работает как поиск. Поля в actor.json:
- `seoTitle`: "Platform + Function + Usecase" → "Skool AI Lead Finder - Buy Signal Detector"
- `seoDescription`: до 160 символов с ключевыми словами
Без этого — нулевой органический трафик навсегда.

### 7. Free актор = нет доверия
75% топ-20 акторов — платные PPE. Начинать с $0 = "почти невозможно восстановиться".
Минимум: $0.001/result с первого дня.

### 8. Maintenance flag = -60-80% видимости
Если актор падает → Apify помечает "needs maintenance" за 7 дней → обвал в Store.
Нужен мониторинг: GitHub Actions или cron который проверяет что актор отдаёт данные.

### 9. README = продающая страница
Обязательно:
- Секция "Quick Start" с конкретным примером
- Пример Output JSON
- Таблица Input параметров
- Ограничения (что НЕ умеет)

## Конкурентные

### 10. Топ акторы недосягаемы лобово
Топ 20 имеют 45K–324K users. Store алгоритм их поднимает автоматически.
Стратегия: underserved niches (<500 competing users) — именно там "Skool AI Lead Hunter".

## Чеклист перед публикацией

- [ ] Дефолтный запуск работает без настройки
- [ ] seoTitle содержит платформу и функцию
- [ ] seoDescription до 160 символов
- [ ] PPE pricing настроен
- [ ] README с Quick Start
- [ ] Input schema с описаниями и примерами
- [ ] Actor.fail() при пустом результате
- [ ] Протестировано на чистом аккаунте
