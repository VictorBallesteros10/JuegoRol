import threading
from app.controller.Servidor import app
from app.view.Main import iniciar_juego

def lanzar_flask():
    app.run(debug=True, port=8080, use_reloader=False)

if __name__ == "__main__":
    print("Iniciando servidor Flask y juego de rol...")

    flask_thread = threading.Thread(target=lanzar_flask)
    flask_thread.start()

    iniciar_juego()
