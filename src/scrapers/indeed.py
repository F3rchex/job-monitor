import time
from typing import List, Dict
from bs4 import BeautifulSoup

# Selenum con anti deteccion
import undetected_chromedriver as uc

# Importar notificador para alertas
from src.telegram.notifier import TelegramNotifier


class Indeed:
    BASE_URL_INDEED = "https://es.indeed.com/jobs?q=python&l=Madrid"

    def __init__(self):
        # Ya no usamos requests.Session porque usamos Selenium
        # Configuramos las opciones de Chrome
        self.chrome_options = uc.ChromeOptions()

        # Modo headless: Chrome se ejecuta sin ventana visible
        self.chrome_options.add_argument('--headless')

        # Opciones para evitar problemas en servidores/Docker
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_argument('--remote-debugging-port=9222')
        self.chrome_options.add_argument('--window-size=1920,1080')

        # User-Agent para parecer más humano
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36')

    def _get_driver(self):
        """Crea una instancia del navegador Chrome anti-detección"""
        driver = uc.Chrome(options=self.chrome_options, version_main=150)
        return driver

    def parse_offers_indeed(self, soup) -> Dict:
        try:
            # Titulo y Link
            title_element = soup.find('h3', class_='jobTitle')
            title_link = title_element.find('a') if title_element else None
            title_span = title_link.find('span') if title_link else None

            title = title_span.get_text(strip=True) if title_span else 'Unknown'
            link = 'https://es.indeed.com' + title_link['href'] if title_link and title_link.has_attr('href') else 'Link no disponible'

            # Empresa
            empresa_element = soup.find('span', {'data-testid':'company-name'})
            empresa_name = empresa_element.get_text(strip=True) if empresa_element else 'Unknown'

            # Ubicacion
            ubicacion_element = soup.find('div', {'data-testid':'text-location'})
            ubicacion = ubicacion_element.get_text(strip=True) if ubicacion_element else 'Ubicacion no definida'

            # Metadatos opcionales
            metadata_list = []
            metadata_ul = soup.find('ul', class_='metadataContainer')
            if metadata_ul:
                metadata_spans = metadata_ul.find_all('span', class_='css-zydy3i')
                metadata_list = [span.get_text(strip=True) for span in metadata_spans]

            return {
                'title': title,
                'empresa': empresa_name,
                'ubicacion': ubicacion,
                'metadata': metadata_list,  # Lista con datos varios
                'link': link
            }

        except Exception as e:
            print(f'No se pudieron obtener los datos de Indeed: {e}')
            return None


    def scrape(self) -> List[Dict]:
        driver = None
        try:
            print(f"Obteniendo ofertas de Indeed con Selenium...")

            # 1. Crear el navegador Chrome
            driver = self._get_driver()

            # 2. Navegar a la URL (como un humano)
            driver.get(self.BASE_URL_INDEED)

            # 3. Esperar a que cargue la página (importante para JavaScript)
            print("Esperando a que cargue la página...")
            time.sleep(10)  # Espera 10 segundos para que cargue todo
            
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            
            # 4. Obtener el HTML final (después de que JavaScript lo modifique)
            page_source = driver.page_source
            
            print(f"DEBUG: HTML length: {len(page_source)} caracteres")
            print(f"DEBUG: ¿Contiene 'cardOutline'? {('cardOutline' in page_source)}")

            # 5. Parsear con BeautifulSoup (como antes)
            soup = BeautifulSoup(page_source, 'html.parser')

            # 6. Buscar las tarjetas de ofertas
            ofertas_cards = soup.find_all('div', class_='cardOutline')

            print(f"Se encontraron {len(ofertas_cards)} ofertas")

            # 7. Parsear cada oferta
            ofertas = []
            for card in ofertas_cards:
                oferta = self.parse_offers_indeed(card)
                if oferta:
                    ofertas.append(oferta)

            return ofertas

        except Exception as e:
            error_msg = f"Error inesperado en Indeed: {e}"
            print(error_msg)

            # Alertar inmediatamente por Telegram
            try:
                notifier = TelegramNotifier()
                notifier.send_error(f"ERROR en scraper Indeed:\n\n{str(e)}")
                print("OK: Error de Indeed notificado a Telegram")
            except Exception as telegram_error:
                print(f"ERROR: No se pudo enviar alerta a Telegram: {telegram_error}")

            return []

        finally:
            # IMPORTANTE: Siempre cerrar el navegador
            if driver:
                driver.quit()
                print("Navegador cerrado correctamente")
