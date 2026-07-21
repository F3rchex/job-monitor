#!/usr/bin/env python3
"""
Script principal del monitor de empleos
Scrapea ofertas, detecta nuevas y envía notificación a Telegram
"""
from src.scrapers.scraper import JobScraper
from src.telegram.notifier import TelegramNotifier


def main():
    print("Iniciando Monitor de Empleos...\n")

    # 1. Crear instancias
    scraper = JobScraper()
    notifier = TelegramNotifier()

    # 2. Detectar ofertas nuevas (scrapea y compara con anterior)
    nuevas = scraper.get_new_offers()

    # 3. Enviar notificación a Telegram
    total_nuevas = len(nuevas['infojobs']) + len(nuevas['indeed'])

    if total_nuevas > 0:
        print(f"\nEnviando {total_nuevas} ofertas nuevas a Telegram...")
        exito = notifier.notify_new_offers(nuevas)

        if exito:
            print("OK: Notificación enviada correctamente a Telegram")
        else:
            print("ERROR: Error al enviar notificación a Telegram")
    else:
        print("\nOK: No hay ofertas nuevas desde el último scraping")
        print("   No se enviará notificación a Telegram")

    print("\nProceso completado")


if __name__ == "__main__":
    main()
