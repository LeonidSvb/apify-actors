# Анатомия Apify актора
Дата: 2026-06-04

---

## Полная структура файлов

```
actors/skool-community-finder/
│
├── .actor/                         ← КОНФИГ (читает Apify)
│   ├── actor.json                  ← Метаданные: имя, версия, память, путь к README
│   ├── INPUT_SCHEMA.json           ← UI форма ввода + валидация
│   └── input.json                  ← Локальный тестовый input (в .gitignore!)
│
├── src/                            ← КОД
│   ├── __init__.py                 ← Точка входа (вызывает main())
│   ├── main.py                     ← Вся логика актора
│   └── utils.py                    ← Shared helpers: _meta, errors, validation
│
├── Dockerfile                      ← Как собрать контейнер
├── requirements.txt                ← Python зависимости
├── README.md                       ← СТРАНИЦА В STORE (маркетинг!)
└── CHANGELOG.md                    ← История версий
```

---

## Каждый файл: зачем нужен

### `.actor/actor.json` — технический паспорт

```json
{
  "actorSpecification": 1,
  "name": "skool-community-finder",    // ← slug в Store URL
  "title": "Skool Community Finder",   // ← отображаемое название
  "version": "0.1",
  "buildTag": "latest",
  "readme": "./README.md",             // ← откуда берёт текст Store страницы
  "input": "./.actor/INPUT_SCHEMA.json",
  "changelog": "./CHANGELOG.md",
  "defaultMemoryMbytes": 512,          // ← сколько RAM по дефолту
  "minMemoryMbytes": 256,
  "maxMemoryMbytes": 2048              // ← потолок памяти
}
```

Важно: `name` = slug в URL актора. После первого `apify push` нельзя менять.

---

### `.actor/INPUT_SCHEMA.json` — форма ввода в Console

Это JSON Schema с Apify расширениями. Определяет:
- Какие параметры у актора
- Какой тип каждого (string/integer/boolean/array/object)
- Дефолтные значения
- UI редактор (textarea, proxy, requestListSources, checkbox)
- Валидацию с понятными ошибками

**Типы editors:**
| Editor | Когда использовать |
|---|---|
| `requestListSources` | Список URL (стандартный для Apify) |
| `proxy` | Прокси конфиг (рендерит специальный UI) |
| `textfield` | Одна строка |
| `textarea` | Длинный текст |
| `number` | Числа с min/max |
| `checkbox` | Boolean |
| `select` | Enum с вариантами |

**prefill vs default:**
- `prefill` — заполняет UI поле, но не используется в API/CLI вызовах
- `default` — используется когда параметр вообще не передан
- `required` — выдаёт ошибку если не передан

---

### `Dockerfile` — контейнер

```dockerfile
FROM apify/actor-python:3.12   # Apify base image: slim Debian + Python

COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY --chown=myuser:myuser . ./   # --chown обязателен!

CMD python3 -m src               # запускает src/__init__.py
```

**Доступные base images:**
- `apify/actor-python:3.12` — только HTTP (httpx, requests). Наш выбор.
- `apify/actor-python-playwright:3.12` — полный браузер, тяжелее, дороже
- `apify/actor-python-selenium:3.12` — Chrome + Selenium

Skool работает через HTTP API (__NEXT_DATA__) — браузер не нужен, берём slim image.

---

### `src/main.py` — логика актора

**Обязательный паттерн:**
```python
async with Actor:                           # инициализация + cleanup
    inp = await Actor.get_input() or {}    # читает input
    await Actor.set_status_message("...")  # показывает прогресс в Console
    await Actor.push_data({...})           # записывает результат в Dataset
    await Actor.charge(event_name="x")    # PPE биллинг
    await Actor.fail(status_message="...") # явный fail с причиной
```

**SDK методы которые используем:**
| Метод | Что делает |
|---|---|
| `Actor.get_input()` | Читает input (из Console или .actor/input.json локально) |
| `Actor.set_status_message(text)` | Текст виден юзеру в Console во время рана |
| `Actor.push_data(item)` | Добавляет запись в Dataset |
| `Actor.charge(event_name, count)` | PPE биллинг — снимает с юзера |
| `Actor.fail(status_message)` | Завершает ран с ошибкой (виден юзеру) |
| `Actor.log.info/warning/error` | Логи (видны в Console > Log tab) |
| `Actor.create_proxy_configuration()` | Настраивает прокси из input |
| `Actor.config.actor_run_id` | ID текущего рана |
| `Actor.open_key_value_store(name)` | KV store для dedup |

---

### `README.md` — главный маркетинговый документ

Это буквально страница актора в Apify Store. Написанный текст = то что юзер видит до покупки.

**Структура (основана на анализе топ акторов):**
```
1. Название + одна строка что делает
2. Quick Start — рабочий copy-paste input
3. What you get — реальный пример output JSON
4. Cost calculator — "$5 кредитов = ~1000 results"
5. Input parameters — таблица всех параметров
6. How it works — 3-4 строки техники
7. Limitations — честно что не работает
8. Use cases — 5 конкретных сценариев
9. FAQ — 5 вопросов включая "cookies?", "0 results?"
10. Related actors — ссылки на свои другие 3 актора
```

Зачем каждая секция важна:
- **Quick Start** — снижает барьер входа, юзер сразу видит результат
- **Cost calculator** — убирает страх "сколько это будет стоить?" (Instagram scraper делает это, у других нет)
- **Limitations** — предотвращает 1-звёздные отзывы "didn't work for private communities"
- **Related actors** — cross-promotion, повышает LTV юзера

---

### `CHANGELOG.md` — история версий

Нужен для:
- Юзеры видят что актор обновляется (активная поддержка = доверие)
- При breakage: "check changelog first" в README
- Semver: 0.1.0 → 0.1.1 (bugfix), 0.1.0 → 0.2.0 (new feature)

---

## Жизненный цикл актора

```
Ты пишешь код в GitHub
        ↓
git push → GitHub Actions → apify push
        ↓
Apify билдит Docker контейнер (~2 мин)
        ↓
Юзер кликает "Run" в Console
        ↓
Apify запускает контейнер:
  Actor.get_input() ← читает что ввёл юзер
  scraping loop     ← основная работа
  Actor.push_data() → записывает в Dataset
  Actor.charge()    → списывает PPE с юзера
        ↓
Ран завершается, Dataset доступен для скачивания
```

---

## PPE биллинг: как работает

**Что настраивается через Apify Console** (не через код):
- Start fee: $0.005 (списывается за каждый ран, даже пустой)
- Per-event fee: $0.003 per "community-scraped"

**Что делает код:**
```python
await Actor.charge(event_name="community-scraped", count=1)
# Apify автоматически списывает configured per-event fee с юзера
```

**Формула прибыли:**
```
revenue = start_fee + (events × per_event_fee)
profit  = 0.8 × revenue - platform_usage_costs
```

Platform usage costs = compute units + residential proxy traffic (платит юзер, но вычитается из твоей доли при PPE модели — уточнить в Apify Dashboard).

---

## Шаблон → готовый актор: что менять

При копировании `_template/` для нового актора:

- [ ] `actor.json`: поменять `name`, `title`
- [ ] `INPUT_SCHEMA.json`: добавить специфичные параметры, поменять `prefill`
- [ ] `src/main.py`: реализовать `scrape_one()`, поменять `ACTOR_NAME`, `PPE_EVENT`
- [ ] `src/utils.py`: добавить специфичные parser функции
- [ ] `README.md`: заполнить все `{{PLACEHOLDER}}` секции
- [ ] `CHANGELOG.md`: поставить дату
- [ ] Добавить `.gitignore` (скопировать из template)
