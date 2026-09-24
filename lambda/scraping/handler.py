import json
import sys
import os

# Hack para importar desde src/ (dos niveles arriba)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scrapers.scraper import JobScraper
from src.telegram.notifier import TelegramNotifier
from src.storage.json_storage import JSONStorage


def lambda_handler(event, context):
    
    print("INFO: Iniciando scraping job desde Lambda")

    # Inicializar componentes con storage S3
    scraper = JobScraper(storage_type='s3')
    notifier = TelegramNotifier()

    try:
        # Ejecutar scraping (mismo código que main.py)
        print("INFO: Ejecutando scraping...")
        nuevas = scraper.get_new_offers()

        total_nuevas = len(nuevas['infojobs']) + len(nuevas['tecnoempleo'])

        print(f"INFO: Ofertas nuevas encontradas: {total_nuevas}")
        print(f"  - InfoJobs: {len(nuevas['infojobs'])}")
        print(f"  - TecnoEmpleo: {len(nuevas['tecnoempleo'])}")

        # Notificar si hay nuevas ofertas
        if total_nuevas > 0:
            print("INFO: Enviando notificación a Telegram...")
            exito = notifier.notify_new_offers(nuevas)

            if exito:
                print("OK: Notificación enviada correctamente")
            else:
                print("ERROR: Fallo al enviar notificación Telegram")
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': 'Scraping OK, pero fallo notificación',
                        'nuevas_ofertas': total_nuevas
                    })
                }
        else:
            print("INFO: No hay ofertas nuevas, no se envía notificación")

        # Return exitoso
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Scraping completado exitosamente',
                'nuevas_ofertas': total_nuevas,
                'infojobs': len(nuevas['infojobs']),
                'tecnoempleo': len(nuevas['tecnoempleo'])
            })
        }

    except Exception as e:
        # Manejo de errores
        print(f"ERROR: Excepción en lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error en scraping',
                'error': str(e)
            })
        }
