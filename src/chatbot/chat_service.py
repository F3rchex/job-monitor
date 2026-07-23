import json
from src.chatbot.openai_client import OpenAIClient
from datetime import datetime
from src.storage.json_storage import JSONStorage

class ChatService:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.storage = JSONStorage()
        #historial de conversacion
        self.messages = []

        
    def load_job_offers(self):
        try:
            offers = self.storage.get_all_offers_from_latest()
            return offers
        except Exception as e:
            print(f'No se pudieron cargar ofertas')
            return {'infojobs':[], 'indeed':[]}
    
    #convertimos json en texto para el mensaje system del LLM, NECESARIO
    def build_context(self, offers): 
        if not offers or (not offers['infojobs'] and not offers['indeed']):
            return "Aun no hay ofertas disponibles"
        
        total_infojobs = len(offers['infojobs'])
        total_indeed = len(offers['indeed'])
        total_offers = total_indeed + total_infojobs
        
        context = f"Tienes acceso a {total_offers} ofertas de trabajo:\n"
        
        if total_infojobs > 0:
            context += f'\nINFOJOBS: {total_infojobs} ofertas\n'
            for i, offer in enumerate(offers['infojobs'], 1):
                context += self._format_offer(i, offer, 'infojobs')
                
        if total_indeed > 0:
            context += f'\nINDEED: {total_indeed} ofertas\n'
            for i, offer in enumerate(offers['indeed'], 1):
                context += self._format_offer(i, offer, 'indeed')
              
        return context
    
    def _format_offer(self, index, offer, source):
        #Campos comunes
        title = offer.get('title', 'No especificado')
        empresa = offer.get('empresa', 'No especificado')
        ubicacion = offer.get('ubicacion', 'No especificado')
        link = offer.get('link','No especificado')
        
        #Construir el texto base con los datos en comun
        texto = f'{index}. {title}\n'
        texto += f' - Empresa: {empresa}\n'
        texto += f' - Ubicacion: {ubicacion}\n'
        
        if source == 'infojobs':
            modalidad = offer.get('modalidad','No especificado')
            contrato = offer.get('contrato','No especificado')
            jornada = offer.get('jornada','No especificado')
            salario = offer.get('salario','No especificado')
        
            texto += f' - Modalidad: {modalidad}\n'
            texto += f' - Contrato: {contrato}\n'
            texto += f' - Jornada: {jornada}\n'
            texto += f' - Salario: {salario}\n'
            
        elif source == 'indeed':
            metadata = offer.get('metadata', [])
            if metadata:
                #Dado que metadata es una lista
                texto += f"   - Info adicional: {', '.join(metadata)}\n"
                
        texto += f' - Fuente: {source}\n'
        texto += f' - Link: {link}\n\n'
        
        return texto
        
    
    def start_conversation(self):
        offers = self.load_job_offers()
        context = self.build_context(offers)
        #Opcional, le damos 'context' para que sepa que datos tenemos, tambien podriamos indicar solo el comportamiento que queremos que tenga.
        system_message = {
            "role": "system",
            "content": f'{context}\n\nEres un asistente que ayuda a buscar y analizar ofertas de empleo de Python en Madrid. Responde de forma clara, concisa y útil. Si el usuario pregunta por una oferta específica, usa el número de la lista.'

        }
        
        #Agregamos al historial
        self.messages.append(system_message)
        
    def chat(self, user_message):
        #1. Agregar mensaje del usuario
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        #2. Obtener tools disponibles
        tools = self.get_available_tools()
        
        #3. Llamar a OpenAI con tools
        response_message = self.openai_client.chat_with_tools(
            messages=self.messages,
            tools=tools
        )
        
        #4. Revisar si hay tool_calls
        if response_message.tool_calls:
            #5. Agregar mensaje assistant con tool_call al historial
            self.messages.append(response_message)
            
            #6. Ejecutar cada función llamada
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                #7. Ejecutar la función
                function_result = self.execute_function(function_name, arguments)
                
                #8. Agregar resultado como mensaje tool
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
            
            #9 . Llamar a OpenAI de nuevo con los resultados
            final_response = self.openai_client.chat_with_tools(
                messages=self.messages,
                tools=tools
            )
            
            #10. Agregar respuesta final al historial
            self.messages.append(final_response)
            
            #11. Devolver el contenido
            return final_response.content
        
        else:
            # No hubo tool_calls, respuesta directa
            self.messages.append(response_message)
            return response_message.content
        
    def save_conversation(self):
        #Generamos nombre de archivo con fecha y nombre
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data/conversations/session_{timestamp}.json"
        
        # Convertir mensajes a diccionarios serializables
        messages_to_save = []
        for msg in self.messages:
            if hasattr(msg, 'model_dump'):  # Es objeto de OpenAI
                messages_to_save.append(msg.model_dump())
            else:  # Ya es dict (mensaje system o user)
                messages_to_save.append(msg)
        
        # Guardar el historial
        with open(filename, "w") as file:
            json.dump(messages_to_save, file, indent=4)
        
        print(f"Conversación guardada correctamente en {filename}")
        
    
    def get_available_tools(self):
        #Devuelve la lista de funciones disponibles para el LLM
        return [
                {
                    "type": "function",
                    "function": {
                        "name": "load_job_offers",
                        "description": "Obtenenemos el ultimo listado de ofertas scrapeado de Infojobs e Indeed.",
                        "parameters": {
                            "type": "object",
                            "properties": {},  # ← Vacío porque no necesita parámetros
                            "required": []
                        }
                    }
                }
        ]
        
    #Segun el nombre de la funcion se ejecuta el código correspondiente
    def execute_function(self, function_name, arguments=None):
        if function_name == "load_job_offers":
            result = self.load_job_offers()
            return result
        else:
            return {"error": f"Función {function_name} no encontrada"}