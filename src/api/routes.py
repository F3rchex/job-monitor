from flask import Blueprint, jsonify
from src.api.auth import require_api_key
from src.scrapers.scraper import JobScraper
from src.telegram.notifier import TelegramNotifier

#Creamos Blueprint para agrupar rutas de la API
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    #Endpoint sin autenticacion para comprobar que la app funciona
    return jsonify({
        "status": "healthy",
        "service": "job_monitor-api"
    }), 200
    

@api_blueprint.route('/trigger-scraping', methods=['POST'])
@require_api_key
def trigger_scrapping():
    #Endpoint protegido con API_KEY
    try:
        print(f'INFO: Iniciando scraping desde endpoint HTTP...')
        scraper = JobScraper()
        notifier = TelegramNotifier()
        
        #Ejecutamos el scraping
        nuevas = scraper.get_new_offers()
        
        total_nuevas = len(nuevas['infojobs']) + len(nuevas['indeed'])
        
        if total_nuevas > 0:
            print(f'INFO: {total_nuevas} ofertas nuevas encontradas')
            exito = notifier.notify_new_offers(nuevas)
            
            if exito:
                print(f'OK: Notificación enviada a Telegram')
                return jsonify({
                    "status": "OK",
                    "nuevas_ofertas": total_nuevas,
                    "notificado": True,
                    "detalles": {
                        "infojobs": len(nuevas['infojobs']),
                        "indeed": len(nuevas["indeed"])
                    }
                }), 200
            else:
                    print("ERROR: Error al enviar notificación a Telegram")
                    return jsonify({
                        "status": "error",
                        "mensaje": "Scraping OK pero fallo envío Telegram"
                    }), 500
        else:
            print("OK: No hay ofertas nuevas")
            return jsonify({
                "status": "ok",
                "nuevas_ofertas": 0,
                "mensaje": "No hay ofertas nuevas desde el último scraping"
            }), 200
            
    except Exception as error:
        #Si algo falla, capturamos el error
        mensaje_error = f"Scraping falló: {str(error)}"
        print(f"ERROR: {mensaje_error}")
        
        #Intentar enviar error a Telegram
        try:
            notifier = TelegramNotifier()
            notifier.send_error(mensaje_error)
            print("OK: Error notificado a Telegram")
        except Exception as error_telegram:
            print(f"ERROR: No se pudo notificar error a Telegram: {str(error_telegram)}")
        
        return jsonify({
            "status": "error",
            "mensaje": mensaje_error
        }), 500