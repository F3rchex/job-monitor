import os
from flask import Flask
from dotenv import load_dotenv
from src.api.routes import api_blueprint

load_dotenv()

app = Flask(__name__)

app.register_blueprint(api_blueprint)

#Ruta raíz (para verificar que funciona)
@app.route('/')
def index():
    return {
        "service": "Job Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "trigger_scraping": "/trigger-scraping (POST, requiere API key)"
        }
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"INFO: Iniciando Job Monitor API en puerto {port}")
    print(f"INFO: Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
