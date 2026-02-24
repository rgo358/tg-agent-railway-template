import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def get_session():
    api_id = int(input("Введи API_ID из my.telegram.org: "))
    api_hash = input("Введи API_HASH из my.telegram.org: ")
    
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start()
    
    session_string = client.session.save()
    print("\n" + "="*50)
    print("✅ Твоя SESSION_STRING:")
    print("="*50)
    print(session_string)
    print("="*50)
    print("Используй эту строку в Railway!")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(get_session())
