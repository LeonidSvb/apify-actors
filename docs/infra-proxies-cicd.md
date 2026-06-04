# Инфраструктура: прокси, локал vs Apify, CI/CD
Дата: 2026-06-04

---

## 1. Кто платит за residential прокси

**Платит ЮЗЕР, не разработчик.**

Это часть "platform usage" — как CPU time и storage. Когда юзер запускает твой актор, Apify списывает с его баланса:
- compute units (CPU/RAM)
- proxy usage (если актор использует Apify Proxy)
- storage operations

Ты как разработчик получаешь **80% от PPE revenue** и не несёшь расходы на прокси юзера.

**Цены на residential прокси (платит юзер):**

| Plan | Цена за GB |
|---|---|
| Starter ($29/мес) | $8.00/GB |
| Scale ($99/мес) | $7.50/GB |
| Business ($299/мес) | $7.00/GB |

**Сколько трафика тратит скраперинг:**
- Одна Skool страница (JSON через __NEXT_DATA__): ~100-300 KB
- 100 комьюнити × 200KB = ~20MB = **$0.16 в residential**
- 1000 постов × 150KB = ~150MB = **$1.20 в residential**

Это немного, но юзер должен об этом знать заранее — иначе "unexpected costs" жалобы.

---

## 2. Нужны ли residential прокси нашим акторам

| Актор | Нужны? | Почему |
|---|---|---|
| Actor 1: Community Finder | Нет для DDG | DDG открытый, datacenter OK |
| Actor 1: probe_community | Да | Skool AWS WAF блокирует datacenter |
| Actor 2: Lookalike | Да | api2.skool.com, WAF |
| Actor 3: Posts Scraper | Да | __NEXT_DATA__ scraping, WAF |
| Actor 4: Profiler | Да | То же самое |

**Правило для INPUT_SCHEMA:** residential proxy как дефолт для всех кроме DDG части Actor 1.

---

## 3. Локальный скрипт vs Apify: почему разница

```
Твой компьютер/сервер:          Apify cloud:
IP = обычный юзер               IP = известный датацентр
WAF: пропускает                 WAF: блокирует → 403/0 results
Нет расходов на прокси          Нужны residential прокси
Не масштабируется               Масштабируется автоматически
Нет PPE биллинга                PPE биллинг работает
```

**Почему Skool блокирует Apify но не тебя:**
- AWS WAF знает ASN (автономные системы) датацентров Apify, AWS, GCP, Azure
- Твой домашний IP или VPS на Hetzner — "чистый", WAF не трогает
- Residential прокси = IP обычного пользователя интернета → WAF не отличает от настоящего браузера

**Практический вывод:**
Если ты тестируешь локально и всё работает → на Apify может ломаться. Всегда тестировать с `APIFY_PROXY_GROUPS=RESIDENTIAL` даже локально.

---

## 4. Одна кодовая база: GitHub → Apify auto-deploy

**Да, это полностью возможно и это единственно правильный подход.**

Структура репо:
```
apify-actors/
├── actors/
│   ├── skool-community-finder/
│   │   ├── .actor/
│   │   │   └── actor.json
│   │   ├── src/
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── skool-lookalike-finder/
│   ├── skool-posts-scraper/
│   └── skool-community-profiler/
└── .github/
    └── workflows/
        ├── deploy-actor1.yml
        ├── deploy-actor2.yml
        ├── deploy-actor3.yml
        └── deploy-actor4.yml
```

**Ты редактируешь только в GitHub. На Apify никогда не трогаешь код.**

---

## 5. GitHub Actions workflow для каждого актора

**Один workflow файл (скопировать × 4, поменять имя папки и секрет):**

`.github/workflows/deploy-actor1.yml`:
```yaml
name: Deploy skool-community-finder

on:
  push:
    branches: [main]
    paths:
      - 'actors/skool-community-finder/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - id: push
        uses: apify/push-actor-action@master
        with:
          token: ${{ secrets.APIFY_TOKEN }}
          working-directory: actors/skool-community-finder

      - run: echo "Deployed build ${{ steps.push.outputs.build-id }} — ${{ steps.push.outputs.build-status }}"
```

**Ключевая строка:** `paths: - 'actors/skool-community-finder/**'`
Деплой срабатывает ТОЛЬКО когда изменился код этого конкретного актора, не остальных.

**Нужен один секрет в GitHub:**
`Settings → Secrets → APIFY_TOKEN` = твой токен из Apify Console

---

## 6. Локальная разработка = тот же код что на Apify

Apify SDK специально сделан так чтобы один код работал везде:

```python
# main.py — одинаково работает локально и на Apify
from apify_client import ApifyClient
from apify import Actor

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        # Локально: Actor читает из .actor/input.json
        # На Apify: Actor читает из Run input
        
        proxy_config = await Actor.create_proxy_configuration(
            groups=["RESIDENTIAL"]
        )
        # Локально: нужен APIFY_TOKEN в .env для прокси
        # На Apify: автоматически
```

**Для локального тестирования:**
```
actors/skool-community-finder/
└── .actor/
    └── input.json   ← тестовый input (в .gitignore!)
```

```json
{
  "keywords": ["python community", "online course"],
  "limit": 10
}
```

---

## 7. Как обновить один скрипт и всё поехало

Сценарий: Skool поменял `__NEXT_DATA__` структуру — ломается Actor 3 и Actor 4.

Твой процесс:
1. Правишь `actors/skool-posts-scraper/src/main.py` локально
2. Тестируешь локально с реальным Skool URL
3. `git push origin main`
4. GitHub Actions автоматически деплоит на Apify
5. Новая версия живёт через ~2 минуты

**Никакого ручного `apify push` не нужно** — только если хочешь задеплоить вне CI.

---

## 8. Синхронизация с исходным скриптом (skool-scrape-signals)

Сейчас у тебя код в двух местах:
- `C:\Users\79818\Desktop\tests\SCRAPING-LEADGEN\skool-scrape-signals\` — оригинал
- `apify-actors/actors/` — Apify версия

**Правильный подход: НЕ синхронизировать, а портировать один раз.**

Логика при портировании:
```
Оригинал (скрипт):              Apify актор:
argparse input         →        Actor.get_input() + INPUT_SCHEMA
print() / logging      →        Actor.log.info() + set_status_message()
суперечка в JSON файл  →        Actor.push_data()
sys.exit(1)            →        Actor.fail()
time.sleep()           →        asyncio.sleep() + rate limiting
ICP segmentation       →        УДАЛИТЬ (в TODO)
keyword scoring        →        УДАЛИТЬ (в TODO)
```

После порта: оригинальный скрипт — архив. Apify актор — единственный источник правды.

---

## 9. Минимальная поддержка после публикации

**Что мониторит себя само:**
- GitHub Actions: если деплой падает → email от GitHub
- Apify: если актор падает с ненулевым кодом → видно в Console
- Actor.fail() при 0 results → юзер видит ошибку, не молчаливый пустой датасет

**Что нужно проверять руками раз в 1-2 недели:**
- Открытые Issues на акторе (Apify Console → Issues tab)
- 1-2 тестовых рана на известных публичных комьюнити

**Когда приходит 0-results issue от юзера:**
- Если Skool поменял структуру → обычно быстрый фикс в одном месте (parser)
- После фикса: `git push` → автодеплой → закрыть issue

**Что НЕ нужно поддерживать:**
- Cookie refresh для юзеров (они сами, README объясняет)
- Proxy management (Apify за тебя)
- Scaling (Apify за тебя)
- Dataset storage (Apify за тебя)

---

## Итоговая схема

```
Ты:          редактируешь код в GitHub
                      ↓
GitHub Actions:  автодеплоит на push
                      ↓
Apify:           хранит актор, запускает по триггеру юзера
                      ↓
Юзер:            платит за compute + residential proxy ($)
                      ↓
Ты:              получаешь 80% от PPE revenue
```
