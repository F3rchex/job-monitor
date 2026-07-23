from src.telegram.bot_handler import main

# Test simple: ejecutar el bot conversacional
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST BOT TELEGRAM CONVERSACIONAL")
    print("="*60)
    print("\nPasos para probar:")
    print("1. Asegurate de que Flask este corriendo (python app.py)")
    print("2. Abre Telegram y busca tu bot")
    print("3. Envia /start para comenzar")
    print("4. Prueba comandos: /ofertas, /help")
    print("5. Prueba preguntas libres: 'Que ofertas hay?'")
    print("\n" + "="*60)
    print()

    main()
