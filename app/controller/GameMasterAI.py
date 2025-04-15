import random

from app.model.Enemigo import Enemigo
from app.utilities.Textos import instrucciones
from app.utilities.Textos import enemigos
from app.view.vista_combate import CombateDialog

class GameMasterAI:
    def __init__(self, ia_instance, jugador):
        self.historia = instrucciones  # Aquí se guarda el historial completo del rol
        self.ia = ia_instance
        self.interacciones = 0
        self.eventos_disponibles = ["combate", "objeto", "nada"]
        self.eventos_usados = []
        self.jugador = jugador

    def narrar_escena(self, texto):
        #La IA genera y describe dinámicamente lo que está pasando en la historia
        self.historia.append({"role": "assistant", "content": texto})
        print(f"este es el prompt{self.historia}")
        respuesta = f"Narrador: {texto} esta es la interaccion {self.interacciones}"
        return respuesta

    def evaluar_evento(self):
       #Decide si ocurre un evento y cuál será, evitando repeticiones hasta que se agoten
        self.interacciones += 1
        if self.interacciones < 2 or 6 < self.interacciones < 9:
            return "nada"
        if len(self.eventos_usados) == len(self.eventos_disponibles):
            self.eventos_usados = []
        eventos_restantes = [e for e in self.eventos_disponibles if e not in self.eventos_usados]
        evento = random.choice(eventos_restantes)
        self.eventos_usados.append(evento)
        return evento

    def activar_evento(self, evento):
        #Ejecuta el evento elegido por la IA
        if evento == "combate":
            prompt = {"role": "user", "content": "Describe un combate emocionante en un juego de rol."}
        elif evento == "objeto":
            prompt = {"role": "user", "content": "Describe el hallazgo de un objeto misterioso en un juego de rol que añada armadura o fuerza."}
        else:
            prompt = {"role": "user", "content": "Describe un momento tranquilo en el que va avanzando la misión y hay una toma de decisiones relevantes para la misión."}

        evento_texto = self.ia.generar_texto(self.historia + [prompt], max_tokens=500)
        respuesta = self.narrar_escena(evento_texto)
        if evento == "combate":
            self.iniciar_combate()
        elif evento == "objeto":
            self.anunciar_descubrimiento()
        return respuesta

    def decidir_proximo_paso(self):
        #Determina qué ocurre a continuación en la historia
        evento = self.evaluar_evento()
        respuesta = self.activar_evento(evento)
        return respuesta

    # def presentar_opciones(self, opciones):
    #     #Muestra opciones al jugador según la situación
    #     print("Tienes las siguientes opciones:")          de momento no lo voy a usar
    #     for i, opcion in enumerate(opciones, 1):
    #         print(f"{i}. {opcion}")

    def resolver_decision_jugador(self, opcion_elegida):
        #Responde a la elección del jugador
        self.historia.append({"role": "user", "content": opcion_elegida})
        self.narrar_escena(f"Has elegido: {opcion_elegida}")
        respuesta=self.decidir_proximo_paso()
        return respuesta

    def describir_entorno(self):
        #Genera dinámicamente una descripción del lugar actual
        prompt = {"role": "user", "content": "Describe el entorno actual de la partida."}
        descripcion = self.ia.generar_texto(self.historia + [prompt], max_tokens=800)
        respuesta= self.narrar_escena(descripcion)
        return respuesta

    def anunciar_descubrimiento(self):
        #Informa al jugador sobre un objeto encontrado de manera dinámica
        prompt = {"role": "user", "content": "Describe un objeto misterioso encontrado."}
        objeto = self.ia.generar_texto(self.historia + [prompt], max_tokens=50)
        self.narrar_escena(f"Has encontrado {objeto}. Puedes recogerlo si lo deseas.")

    def iniciar_combate(self):
        # Ejemplo: se selecciona el enemigo a partir de una lista o diccionario
        enemigo_elegido = enemigos[0]  # Asumiendo que tienes la variable 'enemigos'
        enemigo = Enemigo(
            nombre=enemigo_elegido["nombre"],
            fuerza=enemigo_elegido["fuerza"],
            raza=enemigo_elegido["raza"],
            vida=enemigo_elegido["vida"],
            armadura=enemigo_elegido["armadura"],
            iniciativa=enemigo_elegido["iniciativa"],
            nivel=enemigo_elegido["nivel"]
        )
        combate_dialog = CombateDialog(self.jugador, enemigo)
        combate_dialog.exec()  # Abre el diálogo y espera a que se cierre

        resultado = combate_dialog.get_resultado()
        self.historia.append({"role": "assistant", "content": f"Resultado del combate: {resultado}"})
