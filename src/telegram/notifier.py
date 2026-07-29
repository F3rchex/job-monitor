import asyncio
from typing import List, Dict
from telegram import Bot
from telegram.error import TelegramError
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    # Envía notificaciones de ofertas de empleo a Telegram

    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        # Convertir chat_id a entero (Telegram lo requiere así)
        self.chat_id = int(chat_id or TELEGRAM_CHAT_ID)
        self.bot = Bot(token=self.bot_token)

    def _format_offer(self, oferta: Dict, numero: int) -> str:
        # Formatea una oferta individual
        fuente = "[IJ]" if oferta.get('fuente') == 'InfoJobs' else "[ID]"

        mensaje = f"{fuente} *{numero}. {oferta.get('title', 'Sin título')}*\n"
        mensaje += f"Empresa: {oferta.get('empresa', 'Empresa no especificada')}\n"

        if oferta.get('ubicacion'):
            mensaje += f"Ubicacion: {oferta['ubicacion']}\n"

        if oferta.get('modalidad'):
            mensaje += f"Modalidad: {oferta['modalidad']}\n"

        if oferta.get('contrato'):
            mensaje += f"Contrato: {oferta['contrato']}\n"
        if oferta.get('jornada'):
            mensaje += f"Jornada: {oferta['jornada']}\n"

        if oferta.get('salario') and oferta['salario'] != 'Salario no disponible':
            mensaje += f"Salario: {oferta['salario']}\n"

        if oferta.get('metadata') and oferta['metadata']:
            metadata_text = ", ".join(oferta['metadata'][:3])
            mensaje += f"Info: {metadata_text}\n"

        if oferta.get('link'):
            mensaje += f"[Ver oferta]({oferta['link']})\n"

        return mensaje

    def _create_summary_message(self, nuevas: Dict[str, List[Dict]]) -> str:
        # Crea el mensaje resumen con todas las ofertas nuevas
        total_nuevas = len(nuevas['infojobs']) + len(nuevas['tecnoempleo'])

        mensaje = "*NUEVAS OFERTAS DE EMPLEO*\n"
        mensaje += f"Total: *{total_nuevas}* ofertas nuevas\n"
        mensaje += f"InfoJobs: {len(nuevas['infojobs'])}\n"
        mensaje += f"TecnoEmpleo: {len(nuevas['tecnoempleo'])}\n"
        mensaje += "━━━━━━━━━━━━━━━━━━━━━\n\n"

        if nuevas['infojobs']:
            mensaje += "*INFOJOBS*\n\n"
            for i, oferta in enumerate(nuevas['infojobs'], 1):
                oferta['fuente'] = 'InfoJobs'
                mensaje += self._format_offer(oferta, i)
                mensaje += "\n"

        if nuevas['tecnoempleo']:
            mensaje += "*TECNOEMPLEO*\n\n"
            for i, oferta in enumerate(nuevas['tecnoempleo'], 1):
                oferta['fuente'] = 'TecnoEmpleo'
                mensaje += self._format_offer(oferta, i)
                mensaje += "\n"

        mensaje += "━━━━━━━━━━━━━━━━━━━━━\n"
        mensaje += "_Monitor de Empleos - Python Madrid_"

        return mensaje

    async def send_message(self, text: str) -> bool:
        # Envía un mensaje de texto a Telegram
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return True
        except TelegramError as e:
            print(f"Error al enviar mensaje a Telegram: {e}")
            return False

    async def send_new_offers(self, nuevas: Dict[str, List[Dict]]) -> bool:
        # Envía notificación con las ofertas nuevas
        total_nuevas = len(nuevas['infojobs']) + len(nuevas['tecnoempleo'])

        if total_nuevas == 0:
            print("INFO: No hay ofertas nuevas, no se enviará notificación a Telegram")
            return True

        mensaje = self._create_summary_message(nuevas)

        # Telegram tiene límite de 4096 caracteres por mensaje
        if len(mensaje) > 4000:
            return await self._send_long_message(mensaje)
        else:
            return await self.send_message(mensaje)

    async def _send_long_message(self, mensaje: str) -> bool:
        # Divide y envía mensajes largos en múltiples partes
        partes = mensaje.split('\n\n')
        mensaje_actual = partes[0] + "\n\n"
        exito = True

        for parte in partes[1:]:
            if len(mensaje_actual) + len(parte) > 4000:
                if not await self.send_message(mensaje_actual):
                    exito = False
                mensaje_actual = parte + "\n\n"
            else:
                mensaje_actual += parte + "\n\n"

        if mensaje_actual.strip():
            if not await self.send_message(mensaje_actual):
                exito = False

        return exito

    def notify_new_offers(self, nuevas: Dict[str, List[Dict]]) -> bool:
        # Versión síncrona para usar sin async
        return asyncio.run(self.send_new_offers(nuevas))

    async def send_error_async(self, mensaje_error: str) -> bool:
        #Envio de mensaje de forma asincrona
        try:
            texto = f"*ERROR EN MONITOR DE EMPLEOS*\n\n"
            texto += f"{mensaje_error}\n\n"
            texto += f"_Hora: {self._get_timestamp()}_"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=texto,
                parse_mode='Markdown'
            )
            return True
        except TelegramError as e:
            print(f"ERROR: No se pudo enviar error a Telegram: {e}")
            return False
        
    def send_error(self, mensaje_error: str) -> bool:
        #Envio de mensaje de forma sincrona para usar con Flask
        return asyncio.run(self.send_error_async(mensaje_error))
    
    def _get_timestamp(self) -> str:
        #Obtiene timestamp formateado para España
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")