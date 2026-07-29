import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class JSONStorage:
    #Gestiona el almacenamiento de ofertas en archivos JSON

    def __init__(self, base_dir: str = "."):

        self.base_dir = base_dir
        self.infojobs_dir = os.path.join(base_dir, "data-infojobs")
        self.tecnoempleo_dir = os.path.join(base_dir, "data-tecnoempleo")

        # Crear directorios si no existen
        os.makedirs(self.infojobs_dir, exist_ok=True)
        os.makedirs(self.tecnoempleo_dir, exist_ok=True)

    def _generate_filename(self, source: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{source}_{timestamp}.json"

    def save_offers(self, offers: List[Dict], source: str) -> str:
    
        #Guarda las ofertas en un archivo JSON

        # Determinar directorio según la fuente
        if source.lower() == 'infojobs':
            directory = self.infojobs_dir
        elif source.lower() == 'tecnoempleo':
            directory = self.tecnoempleo_dir
        else:
            raise ValueError(f"Fuente desconocida: {source}. Debe ser 'infojobs' o 'tecnoempleo'")

        # Generar nombre de archivo
        filename = self._generate_filename(source.lower())
        filepath = os.path.join(directory, filename)

        # Preparar datos con metadata
        data = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'count': len(offers),
            'offers': offers
        }

        # Guardar JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def get_latest_file(self, source: str) -> Optional[str]:
        #Obtiene el archivo JSON más reciente de una fuente

        # Determinar directorio
        if source.lower() == 'infojobs':
            directory = self.infojobs_dir
        elif source.lower() == 'tecnoempleo':
            directory = self.tecnoempleo_dir
        else:
            return None

        # Listar archivos JSON
        files = [f for f in os.listdir(directory) if f.endswith('.json')]

        if not files:
            return None

        # Ordenar por fecha (más reciente primero)
        files.sort(reverse=True)

        return os.path.join(directory, files[0])

    def load_offers(self, filepath: str) -> Dict:
        #Carga ofertas desde un archivo JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def get_all_offers_from_latest(self) -> Dict[str, List[Dict]]:

        #Obtiene las ofertas de los archivos más recientes de ambas fuentes
        result = {
            'infojobs': [],
            'tecnoempleo': []
        }

        # InfoJobs
        latest_infojobs = self.get_latest_file('infojobs')
        if latest_infojobs:
            data = self.load_offers(latest_infojobs)
            result['infojobs'] = data.get('offers', [])

        # TecnoEmpleo
        latest_tecnoempleo = self.get_latest_file('tecnoempleo')
        if latest_tecnoempleo:
            data = self.load_offers(latest_tecnoempleo)
            result['tecnoempleo'] = data.get('offers', [])

        return result

    def count_files(self, source: str) -> int:
        #Cuenta cuántos archivos JSON hay de una fuente
        if source.lower() == 'infojobs':
            directory = self.infojobs_dir
        elif source.lower() == 'tecnoempleo':
            directory = self.tecnoempleo_dir
        else:
            return 0

        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        return len(files)
