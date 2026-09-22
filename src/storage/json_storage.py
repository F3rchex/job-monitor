import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class JSONStorage:
    # Almacenamiento de ofertas: local (VPS) o S3 (Lambda)

    def __init__(self, base_dir: str = ".", storage_type: str = "local"):
        self.storage_type = storage_type
        self.base_dir = base_dir

        if storage_type == 'local':
            # Modo VPS: directorios locales
            self.infojobs_dir = os.path.join(base_dir, "data-infojobs")
            self.tecnoempleo_dir = os.path.join(base_dir, "data-tecnoempleo")
            os.makedirs(self.infojobs_dir, exist_ok=True)
            os.makedirs(self.tecnoempleo_dir, exist_ok=True)

        elif storage_type == 's3':
            # Modo Lambda: cliente S3
            import boto3
            self.s3_client = boto3.client('s3')
            self.bucket_name = 'job-monitor-data'

        else:
            raise ValueError(f"storage_type debe ser 'local' o 's3'")

    def _generate_filename(self, source: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{source}_{timestamp}.json"

    def save_offers(self, offers: List[Dict], source: str) -> str:
        # Preparar datos con metadata
        data = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'count': len(offers),
            'offers': offers
        }

        if self.storage_type == 'local':
            # Guardar en disco local (VPS)
            if source.lower() == 'infojobs':
                directory = self.infojobs_dir
            elif source.lower() == 'tecnoempleo':
                directory = self.tecnoempleo_dir
            else:
                raise ValueError(f"Fuente desconocida: {source}")

            filename = self._generate_filename(source.lower())
            filepath = os.path.join(directory, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return filepath

        elif self.storage_type == 's3':
            # Guardar en S3 (Lambda)
            filename = self._generate_filename(source.lower())
            key = f"{source.lower()}/{filename}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )

            return f"s3://{self.bucket_name}/{key}"

    def get_latest_file(self, source: str) -> Optional[str]:
        if self.storage_type == 'local':
            # Listar archivos locales
            if source.lower() == 'infojobs':
                directory = self.infojobs_dir
            elif source.lower() == 'tecnoempleo':
                directory = self.tecnoempleo_dir
            else:
                return None

            files = [f for f in os.listdir(directory) if f.endswith('.json')]

            if not files:
                return None

            files.sort(reverse=True)
            return os.path.join(directory, files[0])

        elif self.storage_type == 's3':
            # Listar objetos en S3
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=f"{source.lower()}/"
                )

                if 'Contents' not in response:
                    return None

                # Ordenar por fecha (más reciente primero)
                objects = sorted(
                    response['Contents'],
                    key=lambda x: x['LastModified'],
                    reverse=True
                )

                return objects[0]['Key'] if objects else None

            except Exception as e:
                print(f"ERROR: No se pudo listar S3: {e}")
                return None

    def load_offers(self, filepath: str) -> Dict:
        if self.storage_type == 'local':
            # Leer archivo local
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

        elif self.storage_type == 's3':
            # Leer desde S3
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=filepath
                )
                content = response['Body'].read().decode('utf-8')
                return json.loads(content)

            except Exception as e:
                print(f"ERROR: No se pudo leer de S3: {e}")
                return {}

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
        if self.storage_type == 'local':
            # Contar archivos locales
            if source.lower() == 'infojobs':
                directory = self.infojobs_dir
            elif source.lower() == 'tecnoempleo':
                directory = self.tecnoempleo_dir
            else:
                return 0

            files = [f for f in os.listdir(directory) if f.endswith('.json')]
            return len(files)

        elif self.storage_type == 's3':
            # Contar objetos en S3
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=f"{source.lower()}/"
                )
                return len(response.get('Contents', []))

            except Exception:
                return 0
