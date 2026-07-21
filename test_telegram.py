import asyncio
from telegram import Bot
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def test_telegram():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    print(f" Verificando configuración...")
    print(f" Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f" Chat ID: {TELEGRAM_CHAT_ID}")
    print()

    try:
        # Obtener info del bot
        bot_info = await bot.get_me()
        print(f" Bot conectado correctamente:")
        print(f"   Nombre: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print()

        # Intentar enviar mensaje de prueba
        print(f" Enviando mensaje de prueba al chat {TELEGRAM_CHAT_ID}...")
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=" *Test de conexión*\n\nSi recibes este mensaje, tu bot funciona correctamente ",
            parse_mode='Markdown'
        )
        print(" Mensaje enviado correctamente")
        print("   Revisa tu Telegram para verificar")

    except Exception as e:
        print(f" Error: {e}")
        print()
        print(" Posibles soluciones:")
        print("  1. Abre Telegram y busca tu bot")
        print("  2. Envíale el comando /start")
        print("  3. Verifica que el CHAT_ID en .env sea correcto")
        print("  4. El CHAT_ID debe ser tu user ID (número), no el username")

if __name__ == "__main__":
    asyncio.run(test_telegram())
