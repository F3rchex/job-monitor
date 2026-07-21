# 🔍 Job Monitor - Monitor de Ofertas de Empleo

Sistema automatizado de scraping que busca ofertas de empleo de Python en Madrid, detecta nuevas ofertas y envía notificaciones diarias a Telegram.

##  Características

-  **Scraping de múltiples fuentes**: InfoJobs e Indeed
-  **Detección inteligente**: Identifica ofertas nuevas comparando por link único
-  **Almacenamiento JSON**: Historial de scraping con timestamp
-  **Notificaciones Telegram**: Mensajes formateados con emojis
-  **Automatización n8n**: (Próximamente)
-  **Chatbot IA con OpenAI**: (Próximamente)

##  Arquitectura del Proyecto

```
job-monitor/
├── src/
│   ├── scrapers/
│   │   ├── infojobs.py      # Scraper InfoJobs (BeautifulSoup)
│   │   ├── indeed.py         # Scraper Indeed (Selenium)
│   │   └── scraper.py        # Orquestador principal
│   ├── storage/
│   │   └── json_storage.py   # Gestión de almacenamiento
│   ├── telegram/
│   │   └── notifier.py       # Notificaciones Telegram
│   └── config.py             # Configuración (tokens, API keys)
├── data-infojobs/            # JSONs de InfoJobs
├── data-indeed/              # JSONs de Indeed
├── main.py                   # Script principal
├── test_scraper.py           # Test de scraping básico
├── test_new_offers.py        # Test de detección de nuevas
└── test_telegram.py          # Test de conexión Telegram
```

##  Instalación

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
# OpenAI (para chatbot IA - próximamente)
OPENAI_API_KEY=tu_api_key_aqui

# Telegram
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

**Cómo obtener las credenciales:**

- **Bot Token**: Habla con [@BotFather](https://t.me/BotFather) en Telegram → `/newbot`
- **Chat ID**: Habla con [@userinfobot](https://t.me/userinfobot) → te dará tu ID

##  Uso

### Script Principal (Recomendado)

Ejecuta scraping, detecta nuevas ofertas y envía a Telegram:

```bash
python main.py
```

### Scripts de Prueba

**Test de scraping básico:**
```bash
python test_scraper.py
```

**Test de detección de ofertas nuevas:**
```bash
python test_new_offers.py
```

**Test de conexión Telegram:**
```bash
python test_telegram.py
```

## 🔧 Componentes Técnicos

### Scrapers

**InfoJobs** (`src/scrapers/infojobs.py`):
- Scraping con BeautifulSoup
- Extrae: título, empresa, ubicación, modalidad, contrato, jornada, salario, link
- Clasificación inteligente de campos por contenido

**Indeed** (`src/scrapers/indeed.py`):
- Scraping con Selenium (Chrome headless)
- Solución al bloqueo 403 de Indeed
- Extrae: título, empresa, ubicación, metadata, link

### Detección de Nuevas Ofertas

El sistema compara ofertas usando el **link como identificador único**:
- InfoJobs: `of-ib711602e534316bab822ce4249ee46`
- Indeed: `jk=7bc5f5f2d189a262`

Usa sets de Python (O(1)) para comparación eficiente.

### Almacenamiento

Guarda JSON con estructura:

```json
{
  "timestamp": "2026-07-10T21:11:44",
  "source": "infojobs",
  "count": 5,
  "offers": [...]
}
```

Archivos: `infojobs_2026-07-10_21-11-44.json`

### Notificaciones Telegram

Formato con emojis:
- 🔵 InfoJobs
- 🟢 Indeed
- 🏢 Empresa
- 📍 Ubicación
- 💼 Modalidad
- 🔗 Link

##  Notas Técnicas

### InfoJobs API

InfoJobs tiene una API oficial, pero el registro está cerrado desde julio 2026. Por eso usamos scraping.

### Indeed y Selenium

Indeed bloquea peticiones HTTP simples (Error 403). Selenium usa un navegador real Chrome headless para evitar detección.

### LinkedIn

LinkedIn no está incluido porque:
- Requiere login obligatorio
- Protección anti-scraping muy agresiva
- Viola términos de servicio
- Complejidad desproporcionada

##  Próximos Pasos

1.  ~~Sistema de scraping funcional~~
2.  ~~Detección de ofertas nuevas~~
3.  ~~Notificaciones Telegram~~
4.  Automatización con n8n (ejecutar cada 6-12 horas)
5.  Chatbot IA con OpenAI (análisis inteligente de ofertas)

##  Requisitos del Sistema

- Python 3.8+
- Chrome/Chromium (para Selenium)
- Conexión a internet

##  Contribuir

Este es un proyecto de aprendizaje personal. No se aceptan contribuciones por el momento.

##  Licencia

Proyecto personal sin licencia definida.

---

**Desarrollado por Fernando Chávez** | Proyecto de portfolio para práctica de scraping y automatización
