# Настройка Apify Developer аккаунта
Дата: 2026-06-04

---

## Один аккаунт или два?

**Один аккаунт.** Apify не требует отдельного "developer" аккаунта.
Твой обычный аккаунт = твой publisher аккаунт. Имя пользователя (username) становится частью URL всех твоих акторов: `apify.com/ТВО_ИМЯ/skool-community-finder`.

Если у тебя уже есть личный аккаунт с каким-то username — он и будет использоваться. Если username некрасивый, лучше создать новый аккаунт сейчас, пока акторы ещё не опубликованы.

**Совет по username:** выбери что-то брендовое и короткое. Примеры: `systemhustle`, `skooltools`, `leoscraper`. Он будет виден всем пользователям в Store.

---

## Шаг 1 — Регистрация

1. Открыть https://apify.com/sign-up
2. Зарегистрироваться (email или Google)
3. Выбрать username — это постоянный выбор, потом не поменяешь без поддержки
4. Подтвердить email

---

## Шаг 2 — Creator Plan ($500 кредитов)

**Зачем:** Creator Plan даёт $500 в platform credits на 6 месяцев + возможность монетизировать акторы через PPE.

1. Открыть https://apify.com/pricing/creator-plan
2. Нажать **Get started for $1/month**
3. Привязать карту, оплатить $1
4. Credits появятся в Console → Billing в течение нескольких минут

**Что получаешь:**
- $500 credits (~33 000 Actor compute units или ~60 GB residential proxy трафика)
- Право публиковать платные акторы в Store
- Доступ к Creator Dashboard с аналитикой revenue

**Важно:** $500 действуют 6 месяцев. После этого нужно продлевать либо купить новый план.

---

## Шаг 3 — API Token для GitHub Actions

Токен нужен чтобы GitHub Actions мог деплоить акторы в твой аккаунт.

1. Открыть https://console.apify.com/settings/integrations
2. В разделе **API tokens** нажать **+ Add new token**
3. Name: `GitHub Actions`
4. Scopes: оставить все галочки (или минимум: Actors → Read + Write)
5. Нажать **Create**
6. Скопировать токен — он показывается один раз

**Добавить в GitHub репозиторий:**
1. Открыть репо на GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Нажать **New repository secret**
3. Name: `APIFY_TOKEN`
4. Secret: вставить токен из шага выше
5. Нажать **Add secret**

---

## Шаг 4 — Первый деплой

### Вариант A: через GitHub (рекомендуется, настраиваем один раз)

```powershell
# Закоммить и запушить — GitHub Actions сам задеплоит
git add actors/skool-community-finder/
git commit -m "add skool-community-finder actor"
git push origin main
```

Через ~3 минуты актор появится в https://console.apify.com/actors

### Вариант B: вручную из терминала (для быстрого теста)

```powershell
# Сначала залогиниться (один раз)
apify login --token ВАШ_ТОКЕН

# Деплоить актор
cd C:\Users\79818\Desktop\apify-actors\actors\skool-community-finder
apify push
```

---

## Шаг 5 — Настройка PPE цен в Console

После первого деплоя нужно настроить цены через UI (нельзя через код).

1. Открыть https://console.apify.com/actors → найти `skool-community-finder`
2. Нажать **Edit** → вкладка **Monetization**
3. Включить **Pay-per-event pricing**
4. Добавить событие:
   - Event name: `community-found`
   - Price per event: `$0.003`
5. Start fee: `$0.005`
6. Сохранить

---

## Шаг 6 — Тест на чистом аккаунте

Перед публикацией проверь что актор работает "из коробки":

1. Console → актор → **Try for free**
2. Нажать **Run with defaults** (без изменения input)
3. Убедиться что есть результаты в Dataset
4. Убедиться что нет ошибок в Log

Это то что видит новый пользователь. Должно работать с нулевой конфигурацией.

---

## Шаг 7 — Публикация в Store

1. Console → актор → **Edit** → вкладка **Publication**
2. Заполнить:
   - **SEO Title:** `Skool Community Finder - Search & Discover Groups by Keywords`
   - **SEO Description** (до 160 символов): `Discover Skool communities by keyword via DuckDuckGo. No login required. Get member count, activity ratio, pricing and more.`
   - **Categories:** Lead Generation, Social Media
3. Загрузить иконку (квадрат 256×256 PNG)
4. Нажать **Publish to Store**

---

## Структура репозитория

```
apify-actors/                    ← один репо для всех акторов
├── actors/
│   ├── skool-community-finder/  ← Actor 1
│   ├── skool-lookalike-finder/  ← Actor 2
│   ├── skool-posts-scraper/     ← Actor 3
│   └── skool-community-profiler/ ← Actor 4
└── .github/workflows/           ← auto-deploy для каждого актора
```

**Монорепо — правильный выбор.** Один репозиторий, один `APIFY_TOKEN` секрет, 4 workflow файла с `paths:` фильтром. Деплоится только тот актор, чей код изменился.

Separate repos нужны только если акторы совершенно независимы и у них разные команды. Для одного разработчика — монорепо удобнее.

---

## Быстрая проверка после деплоя

```powershell
# Проверить что актор задеплоился
apify actor ls

# Запустить тестовый ран прямо из терминала
cd actors/skool-community-finder
apify run
```
