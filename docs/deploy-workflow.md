# Деплой Apify актора — команды и структура

## Установка и логин (один раз)

```bash
npm install -g apify-cli
apify login --token YOUR_APIFY_TOKEN
# токен: Console → Settings → API & Integrations
# хранится в ~/.apify/auth.json — больше не нужно логиниться
```

## Создание нового актора

```bash
apify create skool-lead-hunter
# выбрать: Python
# генерирует: Dockerfile, .actor/, src/main.py, requirements.txt
```

## Структура проекта

```
my-actor/
├── .actor/
│   ├── actor.json          # имя, версия, seoTitle, seoDescription
│   └── INPUT_SCHEMA.json   # форма ввода в UI (обязательно)
├── src/
│   └── main.py             # основная логика
├── Dockerfile              # auto-generated, не трогать без причины
├── requirements.txt
└── README.md               # это страница в Store — продающий текст
```

## Деплой

```bash
cd my-actor/
apify push          # загружает код, билдит Docker на Apify
apify run           # запустить локально (тест без деплоя)
```

## GitHub CI/CD (для автодеплоя)

```yaml
# .github/workflows/deploy.yml
- name: Build on Apify
  run: |
    curl -X POST \
    "https://api.apify.com/v2/acts/YOUR-ACTOR-ID/builds?token=${{ secrets.APIFY_TOKEN }}&waitForFinish=60"
```

## Публикация в Store (отдельный шаг после деплоя)

Console → Actor → Publication tab → заполнить метаданные → Publish to Store

## Ключевые поля actor.json

```json
{
  "name": "skool-lead-hunter",
  "version": "0.0",
  "buildTag": "latest",
  "seoTitle": "Skool AI Lead Finder - Buy Signal Detector",
  "seoDescription": "Find buying signals in Skool communities using AI. Get leads, not raw posts. Under 160 chars."
}
```

## PPE pricing в коде

```python
from apify import Actor
async with Actor:
    inp = await Actor.get_input()
    # ... логика ...
    await Actor.charge("signal-found", 0.005)   # $0.005 за каждый найденный лид
    await Actor.push_data(record)
```
