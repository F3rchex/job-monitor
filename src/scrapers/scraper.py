from typing import List, Dict
from src.scrapers.infojobs import Infojobs
from src.scrapers.indeed import Indeed
from src.storage.json_storage import JSONStorage


class JobScraper:

    def __init__(self, base_dir: str = "."):
        self.infojobs = Infojobs()
        self.indeed = Indeed()
        self.storage = JSONStorage(base_dir=base_dir)

    def scrape_all(self, save_to_json: bool = True) -> Dict[str, List[Dict]]:
        
        resultados = {
            'infojobs': [],
            'indeed': []
        }

        # Scrapear InfoJobs
        try:
            print("\n" + "="*50)
            print("SCRAPEANDO INFOJOBS")
            print("="*50)
            resultados['infojobs'] = self.infojobs.scrape()
            print(f" InfoJobs: {len(resultados['infojobs'])} ofertas obtenidas")

            # Guardar en JSON si está habilitado
            if save_to_json and resultados['infojobs']:
                filepath = self.storage.save_offers(resultados['infojobs'], 'infojobs')
                print(f"  Guardado en: {filepath}")

        except Exception as e:
            print(f" Error en InfoJobs: {e}")

        # Scrapear Indeed
        try:
            print("\n" + "="*50)
            print("SCRAPEANDO INDEED")
            print("="*50)
            resultados['indeed'] = self.indeed.scrape()
            print(f" Indeed: {len(resultados['indeed'])} ofertas obtenidas")

            # Guardar en JSON si está habilitado
            if save_to_json and resultados['indeed']:
                filepath = self.storage.save_offers(resultados['indeed'], 'indeed')
                print(f"  Guardado en: {filepath}")

        except Exception as e:
            print(f" Error en Indeed: {e}")

        # Resumen final
        total = len(resultados['infojobs']) + len(resultados['indeed'])
        print("\n" + "="*50)
        print(f"RESUMEN: {total} ofertas totales")
        print("="*50)

        return resultados

        #Metodos alternativos por si solo quisieramos usar uno
    # def scrape_infojobs_only(self) -> List[Dict]:
    #     """Scrapea solo InfoJobs"""
    #     return self.infojobs.scrape()

    # def scrape_indeed_only(self) -> List[Dict]:
    #     """Scrapea solo Indeed"""
    #     return self.indeed.scrape()

    def get_all_offers_unified(self) -> List[Dict]:
        #Obtiene todas las ofertas en una lista unificada con campo 'fuente'
        resultados = self.scrape_all()
        todas = []

        # Añadir ofertas de InfoJobs
        for oferta in resultados['infojobs']:
            oferta['fuente'] = 'InfoJobs'
            todas.append(oferta)

        # Añadir ofertas de Indeed
        for oferta in resultados['indeed']:
            oferta['fuente'] = 'Indeed'
            todas.append(oferta)

        return todas

    def get_new_offers(self) -> Dict[str, List[Dict]]:
    
        #Detecta ofertas nuevas comparando con el scraping anterior usando el link como identificador
        print("\n" + "="*50)
        print("DETECTANDO OFERTAS NUEVAS")
        print("="*50)

        # 1. Cargar ofertas del scraping ANTERIOR
        previous = self.storage.get_all_offers_from_latest()

        # 2. Verificar si es la primera ejecución
        es_primera_ejecucion = not previous['infojobs'] and not previous['indeed']

        if es_primera_ejecucion:
            print("  Primera ejecución: no hay scraping anterior para comparar")
            print("   Todas las ofertas se considerarán como nuevas\n")

            # Scrapear y devolver todo como nuevo
            current = self.scrape_all(save_to_json=True)
            return current

        # 3. Crear sets de links anteriores (para búsqueda rápida O(1))
        previous_infojobs_links = {oferta.get('link') for oferta in previous['infojobs'] if oferta.get('link')}
        previous_indeed_links = {oferta.get('link') for oferta in previous['indeed'] if oferta.get('link')}

        print(f" Ofertas en scraping anterior:")
        print(f"   InfoJobs: {len(previous_infojobs_links)} ofertas")
        print(f"   Indeed: {len(previous_indeed_links)} ofertas\n")

        # 4. Scrapear ofertas ACTUALES
        current = self.scrape_all(save_to_json=True)

        # 5. Filtrar ofertas nuevas (las que no están en el set de links anteriores)
        nuevas = {
            'infojobs': [
                oferta for oferta in current['infojobs']
                if oferta.get('link') and oferta['link'] not in previous_infojobs_links
            ],
            'indeed': [
                oferta for oferta in current['indeed']
                if oferta.get('link') and oferta['link'] not in previous_indeed_links
            ]
        }

        # 6. Estadísticas
        total_nuevas = len(nuevas['infojobs']) + len(nuevas['indeed'])
        total_duplicadas = (len(current['infojobs']) - len(nuevas['infojobs'])) + \
                          (len(current['indeed']) - len(nuevas['indeed']))

        print("\n" + "="*50)
        print(" ESTADÍSTICAS DE DETECCIÓN")
        print("="*50)
        print(f" Ofertas NUEVAS:")
        print(f"   InfoJobs: {len(nuevas['infojobs'])} nuevas")
        print(f"   Indeed: {len(nuevas['indeed'])} nuevas")
        print(f"   TOTAL: {total_nuevas} nuevas")
        print(f"\n Ofertas DUPLICADAS (ya existían): {total_duplicadas}")
        print("="*50)

        return nuevas
