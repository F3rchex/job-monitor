import os
from flask import Flask
from dotenv import load_dotenv
from src.api.routes import api_blueprint

# Cargar variables de entorno desde .env
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)

# Registrar Blueprint de la API
app.register_blueprint(api_blueprint)

# Ruta raíz (para verificar que funciona)
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
    # Configuración del servidor
    port = int(os.getenv('PORT', 500))  # Railway usa PORT env variable
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"INFO: Iniciando Job Monitor API en puerto {port}")
    print(f"INFO: Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',  # Escucha en todas las interfaces (necesario para Railway)
        port=port,
        debug=debug
    )
