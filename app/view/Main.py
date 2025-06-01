import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from app.controller.IACarga import IA
from app.controller.GameMasterAI import MaestroDeJuegoIA
from app.model.Jugador import Jugador
from app.view.Login import DialogoInicioSesion
from app.view.Partidas_guardadas import DialogoPartidasGuardadas
from app.view.Creador_visual import DialogoCreacionPersonaje
from app.view.interfaz import IUPrincipalJuego
from app.service.GestorBBDD import AdministradorBaseDatosSA

def iniciar_juego(self=None):
    app = QApplication(sys.argv)

    dialogo_login = DialogoInicioSesion()
    if dialogo_login.exec() != QDialog.DialogCode.Accepted:
        sys.exit()
    id_usuario = dialogo_login.id_usuario

    administrador_bd = AdministradorBaseDatosSA()

    dialogo_partidas = DialogoPartidasGuardadas(id_usuario)
    if dialogo_partidas.exec() != QDialog.DialogCode.Accepted:
        sys.exit()
    id_partida = dialogo_partidas.id_partida

    if id_partida:
        datos = administrador_bd.cargar_partida(id_partida)
        duniverso = datos.get("personaje", {})
        universo = duniverso.get("universo", "Mundo de fantasía")
        historia = datos.get("historia", "")
        print(universo)
        datos_personaje = datos.get("personaje", {})
        datos_personaje.pop("universo", None)

        jugador = Jugador(**datos_personaje)
        if jugador.vida <= 0 :
            QMessageBox.warning(self, "Error", "Tu personaje murio y será eliminado, escoja o cree otro.")
            administrador_bd.eliminar_partida(id_partida)
            iniciar_juego()

    else:
        dialogo_crear = DialogoCreacionPersonaje(None)
        if dialogo_crear.exec() != QDialog.DialogCode.Accepted:
            sys.exit()
        datos_personaje = dialogo_crear.obtener_datos_personaje()
        universo = datos_personaje.pop("universo")
        jugador  = Jugador(**datos_personaje)
        administrador_bd.guardar_partida(id_usuario, jugador.nombre, {**datos_personaje, "universo": universo})
        historia = ""

    interfaz_ia = IA()
    interfaz_ia.cargar_modelo()
    maestro     = MaestroDeJuegoIA(interfaz_ia, jugador, universo, id_usuario,historia)

    ventana = IUPrincipalJuego(maestro)
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    iniciar_juego()
