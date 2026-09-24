import json
import sys
import os
import requests

# Hack para importar desde src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.chatbot.chat_service import ChatService

# Variables de entorno
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'


def lambda_handler(event, context):
    print(f"INFO: Telegram webhook recibido")

    try:
        # Parsear body del webhook
        body = json.loads(event.get('body', '{}'))

        if 'message' not in body:
            print("INFO: Webhook sin mensaje, ignorando")
            return {'statusCode': 200}

        message = body['message']
        chat_id = message['chat']['id']

        # Validar que tenga texto
        if 'text' not in message:
            print("INFO: Mensaje sin texto, ignorando")
            return {'statusCode': 200}

        text = message['text']
        username = message.get('from', {}).get('username', 'usuario')

        print(f"INFO: Mensaje de @{username} (chat_id={chat_id}): {text}")

        # Procesar mensaje según tipo
        if text.startswith('/'):
            command = text.split()[0].lower()

            if command == '/start':
                respuesta = handle_start()
            elif command == '/help':
                respuesta = handle_help()
            elif command == '/ofertas':
                respuesta = handle_ofertas()
            else:
                respuesta = "Comando no reconocido. Usa /help para ver comandos disponibles."
        else:
            # Es texto libre, usar ChatService
            respuesta = handle_chat(text)

        # Enviar respuesta a Telegram
        send_message(chat_id, respuesta)

        print(f"OK: Respuesta enviada a chat_id={chat_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }

    except Exception as e:
        print(f"ERROR: Excepción en webhook handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handle_start():
    # Mensaje de bienvenida
    return (
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


def handle_help():
    return (
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


def handle_ofertas():
    return handle_chat("Cuantas ofertas de trabajo hay disponibles?")


def handle_chat(user_message):
    try:
        print(f"INFO: Procesando con ChatService: {user_message}")

        chat_service = ChatService(storage_type='s3')
        chat_service.start_conversation()

        respuesta = chat_service.chat(user_message)

        return respuesta

    except Exception as e:
        print(f"ERROR: ChatService falló: {e}")
        return f"ERROR: No pude procesar tu mensaje. Intenta de nuevo más tarde."


def send_message(chat_id, text):
    url = f'{TELEGRAM_API_URL}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("OK: Mensaje enviado a Telegram")
        else:
            print(f"ERROR: Telegram API respondió con {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"ERROR: No se pudo enviar mensaje a Telegram: {e}")
