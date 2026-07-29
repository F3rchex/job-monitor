import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from src.utils.scraper_utils import get_browser_headers, random_delay


class Infojobs:
    BASE_URL_INFOJOBS = "https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword=python%20madrid&provinceIds=33&searchByType=province&referer=search-filtered&segmentId=&page=1&sortBy=RELEVANCE&onlyForeignCountry=false&countryIds=17&sinceDate=_24_HOURS"

    def __init__(self):
        self.session = requests.Session()
        # Usar headers completos con User-Agent aleatorio
        self.session.headers.update(get_browser_headers())
        
    def parse_offers_infojobs(self, soup) -> Dict:
        try:
            #Titulo
            title_element = soup.find('a', class_='ij-OfferCardContent-description-link sui-PrimitiveLinkBoxLink')
            title = title_element.get_text(strip=True) if title_element else "Unknown"
            
            #Link
            link = "https:" + title_element['href'] if title_element and title_element.has_attr('href') else 'Link no disponible'
            
            #Empresa
            empresa_element = soup.find('a', class_='ij-OfferCardContent-description-subtitle-link')
            empresa = empresa_element.get_text(strip=True) if empresa_element else "Empresa desconocida"
            
            #Obtenemos dos listas (Cabecera y Footer)
            condiciones_list_elements = soup.find_all('ul', class_='ij-OfferCardContent-description-list')
            
            primera_lista = condiciones_list_elements[0].find_all('li')
            
            #Teletrabajo/Hibrido..
            ubicacion = primera_lista[0].get_text(strip=True) if len(primera_lista) > 0 else "Ubicacion no establecida"
            modalidad = primera_lista[1].get_text(strip=True) if len(primera_lista) > 1 else "Modalidad no establecida"
            
            
            #Descripcion del puesto de trabajo
            descripcion_element = soup.find('p', class_='ij-OfferCardContent-description-description ij-OfferCardContent-description-description--hideOnMobile')
            descripcion = descripcion_element.get_text(strip=True) if descripcion_element else "Unknown"
            
            # Segunda lista: extraer todos los elementos y clasificarlos por contenido
            segunda_lista = condiciones_list_elements[1].find_all('li') if len(condiciones_list_elements) > 1 else []

            # Valores por defecto
            contrato = "Contrato no especificado"
            jornada = "Jornada no especificada"
            salario = "Salario no disponible"

            # Clasificar cada elemento según su contenido
            for item in segunda_lista:
                texto = item.get_text(strip=True).lower()

                # Detectar tipo de contrato
                if any(palabra in texto for palabra in ['indefinido', 'temporal', 'formativo', 'autónomo', 'fijo']):
                    contrato = item.get_text(strip=True)

                # Detectar jornada
                elif any(palabra in texto for palabra in ['jornada completa', 'jornada parcial', 'completa', 'parcial']):
                    jornada = item.get_text(strip=True)

                # Detectar salario (contiene € o "salario")
                elif '€' in texto or 'salario' in texto:
                    salario = item.get_text(strip=True)
            
            return {
                'title': title,
                'empresa':empresa,
                'ubicacion': ubicacion,
                'modalidad': modalidad,
                'descripcion':descripcion,
                'contrato':contrato,
                'jornada':jornada,
                'salario':salario,
                'link': link
                
            }
        except Exception as e:
            print(f'Error parseando los datos: {e}')
            return None
            
            
    def scrape(self) -> List[Dict]:
        try:
            print(f"Obteniendo ofertas de InfoJobs...")

            # Delay aleatorio antes del request (simular comportamiento humano)
            random_delay(2, 5)

            response = self.session.get(self.BASE_URL_INFOJOBS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            #Encontrar todas las tarjetas de ofertas
            ofertas_cards = soup.find_all('div', class_='ij-OfferCardContent')
            
            print(f"Se encontraron {len(ofertas_cards)} ofertas")
            
            #Parseamos cada oferta
            ofertas = []
            for card in ofertas_cards:
                oferta = self.parse_offers_infojobs(card)
                if oferta:
                    ofertas.append(oferta)
            
            return ofertas
            
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer petición a InfoJobs: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado en InfoJobs: {e}")
            return []