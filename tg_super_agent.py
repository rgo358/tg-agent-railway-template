import os
import asyncio
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Получаем переменные
SESSION_STRING = os.getenv('SESSION_STRING')
API_ID_STR = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
GROQ_KEY = os.getenv('GROQ_API_KEY')

# Проверяем, что всё есть
if not all([SESSION_STRING, API_ID_STR, API_HASH, GROQ_KEY]):
    logging.error("ОШИБКА: Не все переменные окружения заданы!")
    raise ValueError("Отсутствуют обязательные переменные окружения")
logging.info(f"✅ Groq API Key установлен (бесплатный сервис!)")

try:
    API_ID = int(API_ID_STR)
except ValueError:
    logging.error("API_ID должен быть числом")
    raise

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
groq = OpenAI(api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

chroma = chromadb.PersistentClient(path="./tg_memory_db_v3")
collection = chroma.get_or_create_collection("tg_3months")

async def index_3months():
    try:
        await client.send_message('me', "🔄 Начинаю индексацию за последние 3 месяца...")
        three_months_ago = datetime.now() - timedelta(days=90)
        dialogs = await client.get_dialogs(limit=200)
        for dialog in dialogs:
            entity = dialog.entity
            if isinstance(entity, User):
                continue
            name = getattr(entity, 'title', str(entity.id))
            prefix = "📢 Канал" if getattr(entity, 'broadcast', False) else "👥 Группа"
            async for msg in client.iter_messages(entity, offset_date=three_months_ago, limit=300):
                if not msg.text or len(msg.text.strip()) < 10:
                    continue
                doc_id = f"{entity.id}_{msg.id}"
                if collection.get(ids=[doc_id])['ids']:
                    continue
                emb = embedder.encode(msg.text).tolist()
                collection.add(
                    ids=[doc_id],
                    embeddings=[emb],
                    documents=[msg.text],
                    metadatas=[{"chat": name, "prefix": prefix, "date": msg.date.isoformat()}]
                )
        await client.send_message('me', "✅ База обновлена! Теперь пиши запросы.")
    except Exception as e:
        await client.send_message('me', f"Ошибка индексации: {str(e)}")
        logging.error(f"Индексация ошибка: {str(e)}")

async def analyze(query):
    try:
        results = collection.query(query_texts=[query], n_results=40)
        if not results['documents'][0]:
            await client.send_message('me', "Ничего не нашёл по запросу 😕 Попробуй перефразировать")
            return
        context = "\n".join([f"[{m['prefix']} {m['chat']}] {doc}" for doc, m in zip(results['documents'][0], results['metadatas'][0])])
        try:
            resp = groq.chat.completions.create(
                model="mixtral-8x7b-32k-v0.1",
                messages=[{"role": "user", "content": f"Анализируй по-простому на русском с эмодзи: {query}\nКонтекст из чатов:\n{context[:30000]}"}]
            )
            await client.send_message('me', resp.choices[0].message.content)
        except Exception as groq_err:
            error_msg = str(groq_err)
            if "403" in error_msg or "credit" in error_msg.lower() or "rate" in error_msg.lower():
                await client.send_message('me', f"⚠️ Ошибка Groq API: {error_msg[:150]}\n\nПроверь: https://console.groq.com/")
                logging.error(f"Groq ошибка: {error_msg}")
            else:
                await client.send_message('me', f"❌ Ошибка анализа: {error_msg[:200]}")
                logging.error(f"Groq ошибка: {error_msg}")
    except Exception as e:
        await client.send_message('me', f"❌ Ошибка поиска: {str(e)[:200]}")
        logging.error(f"Анализ ошибка: {str(e)}")

@client.on(events.NewMessage)
async def handler(event):
    me = await client.get_me()
    if event.is_private and event.sender_id == me.id:
        text = event.message.text.lower().strip()
        if any(word in text for word in ["индекс", "обнови", "проиндексир", "загрузи"]):
            await index_3months()
        else:
            await analyze(event.message.text)

async def main():
    try:
        await client.start()
        await client.send_message('me', "✅ TG Agent запущен! (Groq AI - бесплатно)\nПиши в Сохранённые сообщения.\nПримеры: 'обнови', 'что нового в крипте?', 'проанализируй'")
        await index_3months()  # авто-индексация при старте
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Критическая ошибка запуска: {str(e)}")
        if 'client' in locals():
            await client.send_message('me', f"Критическая ошибка запуска: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())
