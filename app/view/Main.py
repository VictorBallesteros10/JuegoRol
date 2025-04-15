import sys

from PyQt6.QtWidgets import QApplication

from app.controller.GameMasterAI import GameMasterAI
from app.controller.IACarga import IA
from app.model.Jugador import Jugador
from app.view.interfaz import GameUI
from app.view.Creador_visual import PlayerCreationDialog

def iniciar_juego():
    app = QApplication(sys.argv)

    # Carga de modelo
    ia = IA()
    ia.cargar_modelo()

    # Diálogo de creación de personaje
    crear_personaje = PlayerCreationDialog(None)
    if crear_personaje.exec():
        datos_jugador = crear_personaje.get_datos_personaje()
        jugador = Jugador(**datos_jugador)

        # Crear GameMasterAI con jugador
        game_master = GameMasterAI(ia_instance=ia, jugador=jugador)

        # Lanzar interfaz de juego
        ventana = GameUI(game_master)
        ventana.show()


        sys.exit(app.exec())
    else:
        print("Creación de personaje cancelada.")
        sys.exit()

if __name__ == "__main__":
    iniciar_juego()
##vamos a poner que pueda elegir donde quiere que se desarrolle su historia pasandole un paramtro al prompt antes de mandarlo