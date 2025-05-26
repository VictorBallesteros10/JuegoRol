import threading
from app.controller.Servidor import app
from app.view.Main import iniciar_juego

def lanzar_flask():
    app.run(debug=True, port=8080, use_reloader=False)

if __name__ == "__main__":
    print("Iniciando servidor Flask y juego de rol...")

    flask_thread = threading.Thread(target=lanzar_flask)
    flask_thread.daemon = True  # Esto es importante para cerrar Flask cuando cierres el juego
    flask_thread.start()

    iniciar_juego()
    #en el turno del enemigo debera ser la ia la que decida que hacer
    #quizas el prompt de despues de la pelea deberia tener contexto de la pelea y de la historia ó que salga una respuesta despues
    #de la pelea y otra de la historia con todo