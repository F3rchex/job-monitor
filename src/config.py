import os
from dotenv import load_dotenv

#Cargar variables del archivo .env
load_dotenv()

#Variables de configuración
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


#Validación: asegurar que los tokens existen
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY no está configurado. "
        "Por favor, añade tu token en el archivo .env"
    )

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no están configurados. "
        "Por favor, añade tus tokens de Telegram en el archivo .env"
    )
