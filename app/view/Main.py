from app.controller.GameMasterAI import GameMasterAI
from app.controller.IACarga import IA
from app.model.Jugador import Jugador
from app.service.creador import crear_jugador_desde_input

def iniciar_juego():
    print("Bienvenido al Juego de Rol")
    ia = IA()
    valores_jugador = crear_jugador_desde_input()
    jugador = Jugador(
        nombre=valores_jugador["nombre"],
        fuerza=valores_jugador["fuerza"],
        raza=valores_jugador["raza"],
        vida=valores_jugador["vida"],
        armadura=valores_jugador["armadura"],
        iniciativa=valores_jugador["iniciativa"],
        experiencia=valores_jugador["experiencia"],
        nivel=valores_jugador["nivel"],
        equipamiento=valores_jugador["equipamiento"]
    )
    ia.cargar_modelo()
    gm = GameMasterAI(ia_instance=ia, jugador=jugador)  # Asegúrate de pasar la instancia de IA
    gm.describir_entorno()
    gm.decidir_proximo_paso()

    while True:
        opcion = input("¿Qué quieres hacer? ")
        gm.resolver_decision_jugador(opcion)
        gm.decidir_proximo_paso()
##vamos a poner que pueda elegir donde quiere que se desarrolle su historia pasandole un paramtro al prompt antes de mandarlo