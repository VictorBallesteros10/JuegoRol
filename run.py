import threading
from app.controller.Servidor import app
from app.view.Main import iniciar_juego

#def lanzar_flask():
#    app.run(debug=True, port=8080, use_reloader=False)

if __name__ == "__main__":
#    print("Iniciando servidor Flask y juego de rol...")

#    flask_thread = threading.Thread(target=lanzar_flask)
#    flask_thread.daemon = True  # Esto es importante para cerrar Flask cuando cierres el juego
#    flask_thread.start()

    iniciar_juego()
#De momento no es necesario lanzar un servidor por que no se van a querer hacer peticiones
#no lee lo primero de las batallas. y parece que lo que pone narrador de las batallas tampoco se manda por el mismo lado
#eliminar jugadores muertos de la base de datos
#añadir iteación a la persistencia del personaje
