import json
import sys
import os

# Hack para importar desde src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scrapers.scraper import JobScraper
from src.telegram.notifier import TelegramNotifier
from src.chatbot.chat_service import ChatService


def lambda_handler(event, context):
    
    print(f"INFO: API request - {event.get('httpMethod')} {event.get('path')}")

    # Extraer método y path del event de API Gateway
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    # Routing manual (reemplaza decoradores Flask)
    try:
        if path == '/health' and http_method == 'GET':
            return health_handler(event)

        elif path == '/trigger-scraping' and http_method == 'POST':
            return trigger_scraping_handler(event)

        elif path == '/chat' and http_method == 'POST':
            return chat_handler(event)

        else:
            # 404 Not Found
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not Found'})
            }

    except Exception as e:
        print(f"ERROR: Excepción en API handler: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})
        }


def health_handler(event):
    #GET /health - Health check
    print("INFO: Health check")

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'ok', 'service': 'job-monitor-api'})
    }


def trigger_scraping_handler(event):
    #POST /trigger-scraping
    print("INFO: Trigger scraping manual")

    # Inicializar scraper con S3
    scraper = JobScraper(storage_type='s3')
    notifier = TelegramNotifier()

    try:
        nuevas = scraper.get_new_offers()
        total_nuevas = len(nuevas['infojobs']) + len(nuevas['tecnoempleo'])

        print(f"INFO: Scraping completado - {total_nuevas} ofertas nuevas")

        if total_nuevas > 0:
            notifier.notify_new_offers(nuevas)
            print("OK: Notificación enviada")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Scraping completado',
                'nuevas_ofertas': total_nuevas,
                'infojobs': len(nuevas['infojobs']),
                'tecnoempleo': len(nuevas['tecnoempleo'])
            })
        }

    except Exception as e:
        print(f"ERROR: Scraping falló: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Scraping failed', 'message': str(e)})
        }


def chat_handler(event):
    #POST /chat - Chatbot con OpenAI
    print("INFO: Chat request")

    # Parsear body (viene como string JSON)
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')

        if not message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Message required'})
            }

        print(f"INFO: Chat message: {message}")

        chat_service = ChatService(storage_type='s3')
        chat_service.start_conversation()

        response = chat_service.chat(message)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'response': response})
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON'})
        }

    except Exception as e:
        print(f"ERROR: Chat falló: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Chat failed', 'message': str(e)})
        }
