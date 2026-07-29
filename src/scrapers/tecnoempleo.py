import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from src.utils.scraper_utils import get_browser_headers, random_delay


class TecnoEmpleo:
    BASE_URL = "https://www.tecnoempleo.com/ofertas-empleo/madrid/python"

    def __init__(self):
        self.session = requests.Session()

        # Usar headers completos con User-Agent aleatorio
        self.session.headers.update(get_browser_headers())

    def parse_offer_tecnoempleo(self, card) -> Dict:
        try:
            # Titulo y Link
            title_element = card.find('h2', class_='fs18')
            if not title_element:
                title_element = card.find('a', class_='js-oferta-link')

            title = title_element.get_text(strip=True) if title_element else 'Unknown'

            link_element = card.find('a', class_='js-oferta-link')
            link = 'https://www.tecnoempleo.com' + link_element['href'] if link_element and link_element.has_attr('href') else 'Link no disponible'

            # Empresa
            empresa_element = card.find('span', class_='fs16')
            if not empresa_element:
                empresa_element = card.find('strong')
            empresa = empresa_element.get_text(strip=True) if empresa_element else 'Unknown'

            # Ubicacion
            ubicacion_element = card.find('span', class_='fs13')
            ubicacion = ubicacion_element.get_text(strip=True) if ubicacion_element else 'Madrid'

            # Descripcion (opcional)
            descripcion_element = card.find('div', class_='excerpt')
            descripcion = descripcion_element.get_text(strip=True) if descripcion_element else ''

            # Fecha publicacion (opcional)
            fecha_element = card.find('time')
            fecha = fecha_element.get_text(strip=True) if fecha_element else ''

            # Salario (opcional)
            salario_element = card.find('span', class_='salario')
            salario = salario_element.get_text(strip=True) if salario_element else ''

            return {
                'title': title,
                'empresa': empresa,
                'ubicacion': ubicacion,
                'descripcion': descripcion[:200] if descripcion else '',  # Limitar a 200 caracteres
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
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar tarjetas de ofertas
            # TecnoEmpleo usa diferentes selectores, probaremos varios
            ofertas_cards = soup.find_all('article', class_='oferta')

            if not ofertas_cards:
                ofertas_cards = soup.find_all('div', class_='offer-item')

            if not ofertas_cards:
                ofertas_cards = soup.find_all('li', class_='list-item')

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
