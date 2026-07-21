import os
from functools import wraps
from flask import request, jsonify



def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #Leer el header Authorization
        auth_header = request.headers.get('Authorization')
        
        #Verificamos que existe el token y de que sea el formato correcto
        if not auth_header:
            return jsonify({"error": "Falta header Authorization"}), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify ({"error": "Formato incorrecto. Usa: Bearer TOKEN"}), 401
        
        #Extraemos el token (quitamos "Bearer")
        token = auth_header.replace('Bearer ', '')
        
        #Obtenemos el API_KEY
        api_key_correcta = os.getenv('API_KEY')
        
        #Comparamos tokens
        if token != api_key_correcta:
            return jsonify({"error":"API key invalida"}), 401
        
        #Si todo esta OK ejecutamos la funcion original
        return f(*args, **kwargs)
    
    return decorated_function
        
        
        