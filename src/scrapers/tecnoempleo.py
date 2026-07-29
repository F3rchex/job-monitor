import requests
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from src.utils.scraper_utils import get_browser_headers, random_delay


class TecnoEmpleo:
    BASE_URL = "https://www.tecnoempleo.com/ofertas-trabajo/python/madrid"

    def __init__(self):
        self.session = requests.Session()

        # Usar headers completos con User-Agent aleatorio
        self.session.headers.update(get_browser_headers())

    def parse_offer_tecnoempleo(self, card) -> Dict:
        try:
            # Titulo y Link (dentro del h3.fs-5)
            h3_element = card.find('h3', class_='fs-5')
            title_link = h3_element.find('a') if h3_element else None

            title = title_link.get_text(strip=True) if title_link else 'Unknown'
            link = title_link['href'] if title_link and title_link.has_attr('href') else 'Link no disponible'

            # Empresa (a con class text-primary link-muted)
            empresa_element = card.find('a', class_='text-primary')
            empresa = empresa_element.get_text(strip=True) if empresa_element else 'Unknown'

            # Buscar el span que contiene ubicacion, fecha y salario
            # Este span tiene class "d-block d-lg-none text-gray-800"
            info_span = card.find('span', class_='d-block')

            ubicacion = 'Madrid'
            fecha = ''
            salario = ''

            if info_span:
                # Ubicacion: buscar el <b> dentro del span
                ubicacion_bold = info_span.find('b')
                if ubicacion_bold:
                    ubicacion_text = ubicacion_bold.get_text(strip=True)
                    # Extraer solo ciudad sin modalidad
                    ubicacion = ubicacion_text.split('(')[0].strip() if '(' in ubicacion_text else ubicacion_text

                # El texto completo del span contiene: "Madrid (Híbrido) - 29/07/2026"
                full_text = info_span.get_text(strip=True)

                # Extraer fecha (formato DD/MM/YYYY)
                fecha_match = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
                if fecha_match:
                    fecha = fecha_match.group()

                # Extraer salario (formato: XX.XXX€ - XX.XXX€ b/a)
                salario_match = re.search(r'[\d.]+€\s*-\s*[\d.]+€\s+b/a', full_text)
                if salario_match:
                    salario = salario_match.group()

            # Descripcion (en span con class hidden-md-down)
            descripcion_element = card.find('span', class_='hidden-md-down')
            descripcion = ''
            if descripcion_element:
                # Extraer solo el texto antes de los badges
                desc_text = descripcion_element.get_text(strip=True)
                # Limitar a 200 caracteres
                descripcion = desc_text[:200] if desc_text else ''

            return {
                'title': title,
                'empresa': empresa,
                'ubicacion': ubicacion,
                'descripcion': descripcion,
                'fecha': fecha,
                'salario': salario,
                'link': link
            }

        except Exception as e:
            print(f'Error parseando oferta de TecnoEmpleo: {e}')
            return None

    def scrape(self) -> List[Dict]:
        try:
            print(f"Obteniendo ofertas de TecnoEmpleo...")

            # Delay aleatorio antes del request (simular comportamiento humano)
            random_delay(2, 5)

            # Realizar peticion HTTP
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()

            # Parsear HTML
            # IMPORTANTE: usar response.text para que requests descomprima gzip automáticamente
            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar tarjetas de ofertas
            # Selector correcto basado en la estructura real de TecnoEmpleo
            # Cada oferta está en un div con class 'p-3'
            ofertas_cards = soup.find_all('div', class_='p-3')

            print(f"Se encontraron {len(ofertas_cards)} ofertas")

            # Parsear cada oferta
            ofertas = []
            for card in ofertas_cards:
                oferta = self.parse_offer_tecnoempleo(card)
                if oferta:
                    ofertas.append(oferta)

            return ofertas

        except requests.exceptions.RequestException as e:
            print(f"Error de conexion con TecnoEmpleo: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado en TecnoEmpleo: {e}")
            return []
