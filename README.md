# Job Monitor - Monitor de Ofertas de Empleo

Sistema automatizado de scraping que busca ofertas de empleo de Python en Madrid, detecta nuevas ofertas y envía notificaciones a Telegram.

**ESTADO: EN PRODUCCIÓN** - Arquitectura serverless en AWS Lambda desde septiembre 2026. Scraping automático diario a las 11:00 AM, API REST y bot Telegram conversacional.

## Características

- **Scraping automático**: Scraping diario con EventBridge (11:00 AM Madrid)
- **Múltiples fuentes**: InfoJobs y TecnoEmpleo
- **Anti-detección**: Random delays, User-Agents rotados, headers completos
- **Detección inteligente**: Identifica ofertas nuevas por link único
- **Storage S3**: Historial de scraping en bucket AWS
- **Notificaciones Telegram**: Mensajes push cuando hay ofertas nuevas
- **API REST serverless**: 3 endpoints HTTP con API Gateway
- **Chatbot IA**: Consulta ofertas con OpenAI GPT-4o-mini
- **Bot Telegram**: Webhook con comandos y mensajes libres
- **Infraestructura como código**: SAM (Serverless Application Model)

## Arquitectura del Proyecto

```
job-monitor/
├── lambda/
│   ├── scraping/
│   │   └── handler.py        # EventBridge cron handler
│   ├── api/
│   │   └── handler.py        # API Gateway handler
│   └── telegram/
│       └── handler.py        # Telegram webhook handler
├── src/
│   ├── scrapers/
│   │   ├── infojobs.py       # Scraper InfoJobs
│   │   ├── tecnoempleo.py    # Scraper TecnoEmpleo
│   │   └── scraper.py        # Orquestador principal
│   ├── storage/
│   │   └── json_storage.py   # Storage dual (local/S3)
│   ├── telegram/
│   │   ├── notifier.py       # Notificaciones push
│   │   └── bot_handler.py    # Bot polling (legacy)
│   ├── chatbot/
│   │   ├── openai_client.py  # Cliente OpenAI
│   │   └── chat_service.py   # Servicio chat + function calling
│   └── api/
│       ├── auth.py           # Decorador @require_api_key
│       └── routes.py         # Flask routes (legacy)
├── template.yaml             # SAM infrastructure
├── app.py                    # Flask API (legacy)
└── main.py                   # Script manual (legacy)
```

## Arquitectura de Producción (AWS Lambda)

```
EventBridge (cron: 0 10 * * ? *)
    └─> Lambda: job-monitor-scraping
        └─> Scraping InfoJobs + TecnoEmpleo
            └─> S3: job-monitor-data
                └─> Telegram Notifier (si hay nuevas)

API Gateway
├─> GET  /health
├─> POST /trigger-scraping
└─> POST /chat
    └─> Lambda: job-monitor-api
        └─> ChatService + OpenAI
            └─> S3: job-monitor-data

Telegram API
    └─> Webhook: /telegram-webhook
        └─> Lambda: job-monitor-telegram
            └─> ChatService + OpenAI
                └─> S3: job-monitor-data
```

## Despliegue en Producción

**Infraestructura AWS:**
- **Región:** eu-west-1 (Irlanda)
- **Lambda Functions:** 3 (scraping, api, telegram)
- **S3 Bucket:** job-monitor-data
- **API Gateway:** REST API con stage Prod
- **EventBridge:** Cron diario 11:00 AM Madrid
- **Costo:** ~$0.10/mes (vs $12/mes VPS anterior)

**URLs de producción:**
```
API REST:
https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/health
https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/trigger-scraping
https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/chat

Telegram Webhook:
https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/telegram-webhook

S3 Bucket:
s3://job-monitor-data/
```

## Instalación Local

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

Crea `.env` en la raíz:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789

# API Flask (desarrollo local)
API_KEY=tu_token_seguro
PORT=5001
CHAT_API_URL=http://localhost:5001/chat
```

### 5. Instalar AWS SAM CLI

```bash
brew install aws-sam-cli
```

### 6. Configurar AWS credentials

```bash
aws configure
# Ingresar AWS Access Key ID y Secret Access Key
```

## Deploy a AWS Lambda

### Build

```bash
sam build
```

### Deploy

Primera vez (configuración interactiva):
```bash
sam deploy --guided
```

Deploys posteriores:
```bash
sam deploy
```

### Ver logs en tiempo real

```bash
# Scraping job
aws logs tail /aws/lambda/job-monitor-scraping --follow

# API
aws logs tail /aws/lambda/job-monitor-api --follow

# Telegram bot
aws logs tail /aws/lambda/job-monitor-telegram --follow
```

### Invocar Lambda manualmente

```bash
aws lambda invoke --function-name job-monitor-scraping response.json
cat response.json
```

## Uso en Desarrollo Local

### API Flask (legacy)

```bash
python app.py
```

Endpoints:
```bash
# Health check
curl http://localhost:5001/health

# Trigger scraping
curl -X POST http://localhost:5001/trigger-scraping \
  -H "Authorization: Bearer TU_API_KEY"

# Chat
curl -X POST http://localhost:5001/chat \
  -H "Authorization: Bearer TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Cuantas ofertas hay?"}'
```

### Bot Telegram (legacy - polling)

```bash
python src/telegram/bot_handler.py
```

Comandos:
- `/start` - Bienvenida
- `/help` - Ayuda
- `/ofertas` - Resumen ofertas
- Mensajes libres: "Que ofertas hay de senior?"

### Script manual

```bash
python main.py
```

## Uso en Producción (AWS)

### API REST

```bash
# Health check
curl https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/health

# Trigger scraping manual
curl -X POST https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/trigger-scraping

# Chat
curl -X POST https://zxf1jojs42.execute-api.eu-west-1.amazonaws.com/Prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Cuantas ofertas hay?"}'
```

### Bot Telegram

Bot activo 24/7 con webhook. Enviar mensaje directo al bot en Telegram:
- `/start` - Bienvenida
- `/help` - Ayuda
- `/ofertas` - Resumen ofertas
- Mensajes libres: "Muestrame ofertas remotas"

### Ver archivos en S3

```bash
# Listar todos los archivos
aws s3 ls s3://job-monitor-data/ --recursive

# Descargar archivo específico
aws s3 cp s3://job-monitor-data/infojobs/infojobs_2026-09-24_11-00-00.json .
```

## Configuración Telegram Webhook

El webhook ya está configurado. Para cambiarlo:

```bash
# Configurar webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://zxf1jojs42.../telegram-webhook"}'

# Verificar webhook
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Borrar webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

## Stack Tecnológico

**Backend:**
- Python 3.12
- OpenAI 1.35.0 (GPT-4o-mini)
- BeautifulSoup4 4.15.0
- python-telegram-bot 22.8 (legacy)
- requests 2.32.3

**AWS:**
- Lambda (Python 3.12 runtime)
- S3 (storage)
- API Gateway (REST API)
- EventBridge (cron scheduler)
- CloudWatch (logs)
- IAM (permissions)

**Infraestructura:**
- AWS SAM (Serverless Application Model)
- CloudFormation (bajo el capó)

**Desarrollo local (legacy):**
- Flask 3.0.3

## Notas Técnicas

**Scrapers:**
- InfoJobs: BeautifulSoup (API cerrada julio 2026)
- TecnoEmpleo: BeautifulSoup (menos protección anti-bot)
- Indeed: Descartado (anti-bot agresivo)
- LinkedIn: No viable (requiere login, viola ToS)

**Anti-detección:**
- Random delays (2-5s entre requests)
- User-Agent rotation (6 variantes)
- Headers completos (11 headers navegador real)
- Session persistence (mantiene cookies)

**Storage dual:**
- Local: `storage_type='local'` (desarrollo)
- S3: `storage_type='s3'` (producción Lambda)

**Bot Telegram:**
- VPS legacy: polling con `run_polling()`
- Lambda producción: webhook HTTP
- Solo uno puede estar activo (Telegram API limita)

## Migración VPS → Lambda

**Antes (VPS DigitalOcean):**
- Servidor corriendo 24/7
- n8n para scheduling
- Costo: $12/mes

**Después (AWS Lambda):**
- Pay-per-use (solo cuando se ejecuta)
- EventBridge para scheduling
- Costo: ~$0.10/mes

**Ahorro:** $11.90/mes = $142.80/año

## Comandos Útiles

**SAM:**
```bash
sam build                    # Compilar
sam deploy                   # Desplegar
sam logs -n ScrapingFunction # Ver logs
sam local invoke             # Test local
```

**AWS CLI:**
```bash
aws lambda list-functions    # Listar Lambdas
aws s3 ls s3://job-monitor-data/ --recursive  # Ver S3
aws logs tail /aws/lambda/job-monitor-scraping --follow  # Logs tiempo real
```

**Git:**
```bash
git status
git add .
git commit -m "feat: descripción"
git push origin main
```

---

**Desarrollado por Fernando Chávez** | Proyecto portfolio - Scraping, automatización y arquitectura serverless
