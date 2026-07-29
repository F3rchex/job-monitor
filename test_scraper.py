from src.scrapers.scraper import JobScraper

# Crear el orquestador
scraper = JobScraper()

# Opción 1: Obtener todas las ofertas separadas por fuente
resultados = scraper.scrape_all()
print(f"\nInfoJobs: {len(resultados['infojobs'])} ofertas")
print(f"TecnoEmpleo: {len(resultados['tecnoempleo'])} ofertas")

# Mostrar primera oferta de cada fuente
if resultados['infojobs']:
    print("\n--- Primera oferta de InfoJobs ---")
    print(resultados['infojobs'][0])

if resultados['tecnoempleo']:
    print("\n--- Primera oferta de TecnoEmpleo ---")
    print(resultados['tecnoempleo'][0])