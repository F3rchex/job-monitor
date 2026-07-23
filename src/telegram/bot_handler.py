import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuracion
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
CHAT_API_URL = os.getenv('CHAT_API_URL', 'http://localhost:5001/chat')


# Llama al endpoint /chat de Flask con el mensaje del usuario
def call_chat_api(user_message: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "message": user_message
        }

        response = requests.post(
            CHAT_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Sin respuesta del chatbot')
        else:
            return f"ERROR: El chatbot respondio con codigo {response.status_code}"

    except requests.exceptions.Timeout:
        return "ERROR: El chatbot tardo demasiado en responder (timeout)"
    except requests.exceptions.ConnectionError:
        return "ERROR: No se pudo conectar con el chatbot. Verifica que Flask este corriendo."
    except Exception as e:
        return f"ERROR: {str(e)}"


# Handler para el comando /start
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = (
        "Hola Soy el bot de *Monitor de Empleos*\n\n"
        "Puedo ayudarte a consultar ofertas de trabajo de Python en Madrid.\n\n"
        "*Comandos disponibles:*\n"
        "/ofertas - Ver cuantas ofertas hay disponibles\n"
        "/help - Mostrar ayuda\n\n"
        "Tambien puedes escribirme preguntas libremente, por ejemplo:\n"
        "- Que ofertas hay de Python senior?\n"
        "- Cual es la mejor pagada?\n"
        "- Muestrame ofertas remotas\n"
    )

    await update.message.reply_text(
        mensaje_bienvenida,
        parse_mode='Markdown'
    )


# Handler para el comando /help
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_ayuda = (
        "*Ayuda - Monitor de Empleos*\n\n"
        "*Comandos:*\n"
        "/start - Mensaje de bienvenida\n"
        "/ofertas - Resumen de ofertas disponibles\n"
        "/help - Esta ayuda\n\n"
        "*Preguntas libres:*\n"
        "Puedes preguntarme lo que quieras sobre las ofertas:\n"
        "- Cuantas ofertas hay?\n"
        "- Que ofertas hay de senior?\n"
        "- Muestrame ofertas con buen salario\n"
        "- Hay ofertas remotas?\n\n"
        "_Powered by OpenAI GPT-4o-mini_"
    )

    await update.message.reply_text(
        mensaje_ayuda,
        parse_mode='Markdown'
    )


# Handler para el comando /ofertas
async def handle_ofertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("typing")

    respuesta = call_chat_api("Cuantas ofertas de trabajo hay disponibles?")

    await update.message.reply_text(respuesta)


# Handler para mensajes de texto libres (no comandos)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    await update.message.chat.send_action("typing")

    # Llamar al endpoint /chat
    respuesta = call_chat_api(user_message)

    await update.message.reply_text(respuesta)


def main():
    print("INFO: Iniciando bot de Telegram conversacional...")

    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN no esta configurado en .env")
        return

    if not API_KEY:
        print("ERROR: API_KEY no esta configurado en .env")
        return

    print(f"INFO: Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f"INFO: Chat API URL: {CHAT_API_URL}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("ofertas", handle_ofertas))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("OK: Bot iniciado correctamente. Esperando mensajes...")
    print("INFO: Presiona Ctrl+C para detener el bot")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
