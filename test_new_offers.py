from src.scrapers.scraper import JobScraper


def main():
    # Crear el scraper
    scraper = JobScraper()

    # Detectar ofertas nuevas (compara con el scraping anterior)
    nuevas = scraper.get_new_offers()

    # Mostrar algunas ofertas nuevas si las hay
    if nuevas['infojobs']:
        print("\n Primeras 3 ofertas nuevas de InfoJobs:")
        for i, oferta in enumerate(nuevas['infojobs'][:3], 1):
            print(f"\n{i}. {oferta['title']}")
            print(f"   Empresa: {oferta['empresa']}")
            print(f"   Ubicación: {oferta['ubicacion']}")
            print(f"   Link: {oferta['link']}")

    if nuevas['tecnoempleo']:
        print("\n Primeras 3 ofertas nuevas de TecnoEmpleo:")
        for i, oferta in enumerate(nuevas['tecnoempleo'][:3], 1):
            print(f"\n{i}. {oferta['title']}")
            print(f"   Empresa: {oferta['empresa']}")
            print(f"   Ubicación: {oferta['ubicacion']}")
            print(f"   Link: {oferta['link']}")

    # Resumen final
    total_nuevas = len(nuevas['infojobs']) + len(nuevas['tecnoempleo'])
    if total_nuevas == 0:
        print("\n No hay ofertas nuevas desde el último scraping")
    else:
        print(f"\n Se detectaron {total_nuevas} ofertas nuevas en total")


if __name__ == "__main__":
    main()
