import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_chat():
    """Test del endpoint /chat con autenticación"""

    url = "http://localhost:5001/chat"
    api_key = os.getenv('API_KEY')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": "¿Cuántas ofertas de trabajo hay disponibles?"
    }

    print("\nINFO: Enviando mensaje al chatbot...")
    print(f"   URL: {url}")
    print(f"   Mensaje: {payload['message']}\n")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print("OK: Respuesta exitosa\n")
            print("="*60)
            print("RESPUESTA DEL CHATBOT:")
            print("="*60)
            print(data.get('response'))
            print("="*60)
        else:
            print(f"ERROR: Status code {response.status_code}")
            print(f"Respuesta: {response.text}")

    except requests.exceptions.ConnectionError:
        print("ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que Flask esté corriendo: python app.py")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST CHATBOT - JOB MONITOR")
    print("="*60)
    test_chat()
