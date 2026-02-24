# 🚀 Инструкция по развертыванию на Railway

## Переменные окружения (требуются)

Тебе нужно предоставить 4 переменные:
- `SESSION_STRING` — сессия Telegram
- `API_ID` — из my.telegram.org
- `API_HASH` — из my.telegram.org  
- `XAI_API_KEY` — API ключ от Grok (X.AI)

## Способ 1: One-Click Deploy (самый простой!) ⭐

Нажми на эту ссылку:
```
https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Frgo358%2Ftg-agent-railway-template
```

Railway покажет форму для переменных окружения. Скопируй и вставь значения выше.

**Что произойдет:**
1. Railway создаст новый проект
2. Прочитает `railway.json` с конфигурацией
3. Установит переменные окружения
4. Автоматически создаст Docker контейнер
5. Развернет приложение ✅

---

## Способ 2: Через GitHub + Railway Dashboard

1. Открой https://railway.app/dashboard
2. Нажми **"New Project"**
3. Выбери **"Deploy from GitHub"**
4. Выбери репозиторий `tg-agent-railway-template`
5. Railway автоматически прочитает `railway.json`
6. Введи переменные окружения с экрана выше
7. Нажми **"Deploy"** 🚀

---

## Способ 3: CLI (если Ты опытный)

```bash
# Установи Railway CLI
npm install -g @railway/cli

# Авторизуйся (нужно будет открыть браузер)
railway login

# Перейди в папку проекта
cd /workspaces/tg-agent-railway-template

# Инициализируй проект
railway init

# Установи переменные (можешь использовать значения выше)
railway variables set SESSION_STRING "1ApWapz..."
railway variables set API_ID "31715478"
railway variables set API_HASH "ef2c4e46bea6dae2365472b194f98c86"
railway variables set XAI_API_KEY "xai-OhfxYA..."

# Развертни!
railway up
```

---

## После развертывания

- Railway будет показывать логи в real-time
- Приложение автоматически перезагружается при ошибках (configurable в `railway.json`)
- Следи за прогрессом индексации в логах
- Получай ответы от Grok в Telegram!

---

## Если что-то не работает

1. Проверь логи в Railway Dashboard
2. Убедись что все переменные окружения установлены
3. Проверь что SESSION_STRING валиден (он может истечь)
4. Смотри на https://docs.railway.app/ для помощи

**Готово! Твой TG Agent скоро будет live! 🎉**
