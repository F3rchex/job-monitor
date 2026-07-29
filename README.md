# Job Monitor - Monitor de Ofertas de Empleo

Sistema automatizado de scraping que busca ofertas de empleo de Python en Madrid, detecta nuevas ofertas y envía notificaciones diarias a Telegram.

**ESTADO: EN PRODUCCIÓN** - Desplegado en VPS DigitalOcean, ejecutándose automáticamente cada día a las 11:00 AM desde julio 2026.

## Características

- **Scraping de múltiples fuentes**: InfoJobs y TecnoEmpleo
- **Anti-detección**: Random delays, User-Agents rotados, headers completos
- **Detección inteligente**: Identifica ofertas nuevas comparando por link único
- **Almacenamiento JSON**: Historial de scraping con timestamp
- **Notificaciones Telegram**: Mensajes formateados push
- **API REST Flask**: Endpoints HTTP con autenticación Bearer token
- **Automatización n8n**: Workflow activo ejecutándose diariamente
- **Chatbot IA con OpenAI**: Consulta ofertas con GPT-4o-mini
- **Bot Telegram conversacional**: Comandos y mensajes libres
- **Despliegue en producción**: VPS DigitalOcean con servicios systemd

## Arquitectura del Proyecto

```
job-monitor/
├── src/
│   ├── api/
│   │   ├── auth.py           # Decorador @require_api_key
│   │   └── routes.py         # Endpoints /health, /trigger-scraping, /chat
│   ├── chatbot/
│   │   ├── openai_client.py  # Cliente OpenAI GPT-4o-mini
│   │   └── chat_service.py   # Servicio de chat with function calling
│   ├── scrapers/
│   │   ├── infojobs.py       # Scraper InfoJobs (BeautifulSoup)
│   │   ├── tecnoempleo.py    # Scraper TecnoEmpleo (BeautifulSoup)
│   │   └── scraper.py        # Orquestador principal
│   ├── storage/
│   │   └── json_storage.py   # Gestión de almacenamiento
│   ├── telegram/
│   │   ├── notifier.py       # Notificaciones push
│   │   └── bot_handler.py    # Bot conversacional
│   ├── utils/
│   │   └── scraper_utils.py  # Anti-detección (delays, headers, UA rotation)
│   └── config.py             # Configuración (tokens, API keys)
├── data-infojobs/            # JSONs de InfoJobs
├── data-tecnoempleo/         # JSONs de TecnoEmpleo
├── app.py                    # Servidor Flask API
├── main.py                   # Script principal (ejecución manual)
├── test_chat.py              # Test endpoint /chat
└── test_bot_telegram.py      # Test bot conversacional
```

## Arquitectura de Producción

```
VPS DigitalOcean (Frankfurt)
├── Flask API (puerto 5001)
│   └── systemd service: job-monitor.service
│   └── Endpoints: /health, /trigger-scraping, /chat
│
├── Bot Telegram conversacional
│   └── systemd service: telegram-bot.service
│   └── Comandos: /start, /help, /ofertas + mensajes libres
│
├── n8n (puerto 5678)
│   └── systemd service: n8n.service
│
└── Workflow n8n activo
    └── Schedule Trigger (11:00 AM diario)
        └── HTTP POST /trigger-scraping (con API key)
            └── Scraping → Notificación Telegram
```

## Despliegue en Producción

El proyecto está desplegado en un VPS DigitalOcean:

- **IP pública:** 164.92.138.18
- **API:** http://164.92.138.18:5001
- **n8n:** http://164.92.138.18:5678
- **Región:** Frankfurt (FRA1)
- **Recursos:** 2GB RAM, 1 vCPU, 50GB SSD
- **Coste:** $12/mes

### Servicios configurados

**Flask API (systemd):**
- Auto-arranque al iniciar servidor
- Restart automático si falla
- Logs: `sudo journalctl -u job-monitor`

**Bot Telegram (systemd):**
- Auto-arranque al iniciar servidor
- Restart automático si falla
- Logs: `sudo journalctl -u telegram-bot`

**n8n (systemd):**
- Auto-arranque al iniciar servidor
- Workflow activo con Schedule Trigger
- Logs: `sudo journalctl -u n8n`

### Seguridad

- Usuario no-root con SSH key authentication
- Firewall UFW: solo puertos 22, 5001, 5678 abiertos
- API protegida con Bearer token
- Variables sensibles en archivo .env


## Instalación Local (Desarrollo)

### 1. Clonar repositorio

```bash
git clone <tu-repo>
cd job-monitor
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# OpenAI (chatbot IA)
OPENAI_API_KEY=tu_api_key_aqui

# Telegram
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# API Flask
API_KEY=tu_token_seguro_aqui
PORT=5001
CHAT_API_URL=http://localhost:5001/chat
```

**Cómo obtener las credenciales:**

- **Bot Token**: Hablar con [@BotFather](https://t.me/BotFather) en Telegram → `/newbot`
- **Chat ID**: Hablar con [@userinfobot](https://t.me/userinfobot) → te dará tu ID

## Uso

### API Flask (Producción)

Arranca el servidor Flask API:

```bash
python app.py
```

Endpoints disponibles:
- **GET /health**: Health check (sin autenticación)
- **POST /trigger-scraping**: Ejecuta scraping (requiere API key)
- **POST /chat**: Chatbot conversacional (requiere API key)

Ejemplos de uso:
```bash
# Trigger scraping
curl -X POST http://localhost:5001/trigger-scraping \
  -H "Authorization: Bearer TU_API_KEY"

# Chatbot
curl -X POST http://localhost:5001/chat \
  -H "Authorization: Bearer TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántas ofertas hay?"}'
```

### Bot Telegram Conversacional

Arranca el bot conversacional:

```bash
python test_bot_telegram.py
```

**Comandos disponibles:**
- `/start` - Mensaje de bienvenida
- `/help` - Ayuda
- `/ofertas` - Resumen de ofertas disponibles
- Mensajes libres: "¿Qué ofertas hay de Python senior?"

### Script Principal (Manual)

Ejecuta scraping, detecta nuevas ofertas y envía a Telegram:

```bash
python main.py
```

### API REST Endpoints

- `GET /health` - Health check
- `POST /trigger-scraping` - Ejecuta scraping (requiere API key)
- `POST /chat` - Chatbot conversacional (requiere API key)

## Notas Técnicas

- **InfoJobs:** Scraping con BeautifulSoup (API cerrada desde julio 2026)
- **TecnoEmpleo:** Scraping con BeautifulSoup (portal IT específico, menos protección)
- **Indeed:** Descartado (anti-bot muy agresivo, requiere proxies caros)
- **LinkedIn:** No incluido (requiere login, viola ToS)

### Medidas anti-detección implementadas:
- Random delays (2-5 segundos entre requests)
- User-Agent rotation (6 variantes diferentes)
- Headers completos (11 headers que simulan navegador real)
- Session persistence (mantiene cookies)

## Stack Tecnológico

**Backend:**
- Python 3.12
- Flask 3.0.3 (API REST)
- OpenAI 1.35.0 (GPT-4o-mini)
- BeautifulSoup4 4.15.0 (scraping InfoJobs y TecnoEmpleo)
- python-telegram-bot 22.8 (bot conversacional)

**Automatización:**
- n8n 2.8.4 (workflow automation)
- Node.js 20.20.2

**Infraestructura:**
- Ubuntu 24.04 LTS
- systemd (gestión servicios)
- UFW (firewall)

**Requisitos:**
- Python 3.8+
- Chrome/Chromium (para Selenium)

---

**Desarrollado por Fernando Chávez** | Proyecto de portfolio para práctica de scraping y automatización
