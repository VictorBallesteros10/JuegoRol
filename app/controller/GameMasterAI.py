import random
from app.utilities.Textos import enemigos
from app.service.AccionesCombate import MecanicaCombate
from app.model.Enemigo import Enemigo
from app.service.GestorBBDD import AdministradorBaseDatosSA
from app.service.Gestion_historia import GestionHistoria
from app.utilities.Textos import instrucciones

class MaestroDeJuegoIA:
    def __init__(self, interfaz_ia, jugador, universo: str, id_usuario: int, historia: str = ""):
        self.interfaz_ia         = interfaz_ia
        self.jugador             = jugador
        self.universo            = universo
        self.id_usuario          = id_usuario
        self.dao_partidas        = AdministradorBaseDatosSA()
        self.contador_decisiones = 0
        self.combate_activo      = False
        self.mecanica_combate    = None
        self.enemigo_actual      = None
        self.mision_principal    = None
        self.gestion_historia    = GestionHistoria(interfaz_ia.lmstudio_url)
        self.historia            = historia

    def formatear_narracion(self, texto: str) -> str:
        return f"{texto}"

    def obtener_descripcion_entorno(self) -> str:
        if self.historia: # Si ya hay una historia, la devolvemos
            self.historia=self.gestion_historia.crear_resumen(self.historia)
            return self.historia
        msgs = list(instrucciones)


        # Añade un sistema con la descripción del entorno
        contenido_entorno = (
            f"En el universo de {self.universo}, describe en un solo "
            f"fragmento de prosa el lugar donde comienza {self.jugador.nombre}, "
            f"un {self.jugador.raza}. Hazlo coherente y sin enumerar."
        )
        msgs.append({"role": "system", "content": contenido_entorno})

        # Llama a la IA con la lista de mensajes
        introduccion = self.interfaz_ia.generar_texto(msgs).strip()
        narr_intro = self.formatear_narracion(introduccion)

        # Ahora planteamos misión principal
        msgs = list(instrucciones)
        contenido_mision = (
            "En ese mismo estilo, plantea la misión principal en un solo "
            "fragmento de prosa, coherente y sin enumerar. Indica objetivo "
            "y punto de partida."
        )
        msgs.append({"role": "system", "content": contenido_mision})

        mtxt = self.interfaz_ia.generar_texto(msgs).strip()
        self.mision_principal = mtxt
        narr_mision = self.formatear_narracion(mtxt)

        return f"{narr_intro}\n{narr_mision}"

    def determinar_tipo_evento(self) -> str:
        if self.combate_activo:
            return "combate"
        self.contador_decisiones += 1
        siguiente = self.contador_decisiones
        print(siguiente)
        if siguiente <= 3:
            return "narrativa"
        if siguiente == 4:
            return "objeto"
        if siguiente == 5:
            return "combate"
        if 6 <= siguiente <= 7:
            return "narrativa"
        if siguiente == 8:
            return "combate_final"
        return "final"

    def iniciar_evento(self, tipo_evento: str) -> dict:
        if tipo_evento == "narrativa":
            print(f"estoy en narrativa {self.mision_principal} y {self.gestion_historia.devolver_historia()}")
            prompt = (
                f"Continúa la historia de {self.jugador.nombre} en {self.universo}, teniendo muy en cuenta la decision tomada en la respuesta del jugador "
                f"centrada en {self.mision_principal}. "
                "Escribe un solo fragmento de prosa, coherente y sin enumerar, "
                "con sugerencias sutiles de acción."
            )
            frag = self.interfaz_ia.generar_texto(prompt)
            return {'tipo': 'narrativa', 'texto': self.formatear_narracion(frag)}

        if tipo_evento == "objeto":
            prompt = (
                f"Describe en un solo fragmento de prosa cómo {self.jugador.nombre} "
                f"encuentra un objeto clave para la misión. Sin enumerar, solo el hallazgo con el contexto de {self.gestion_historia.devolver_historia()}"
            )
            desc = self.interfaz_ia.generar_texto(prompt)
            narr = self.formatear_narracion(desc)
            bonus_attr = random.choice(['fuerza','vida','iniciativa'])
            bonus_val  = random.randint(1,3)
            setattr(self.jugador, bonus_attr,
                    getattr(self.jugador, bonus_attr) + bonus_val)
            self.jugador.equipamiento.append(
                f"objeto que otorga +{bonus_val} {bonus_attr}"
            )
            return {
                'tipo': 'objeto',
                'texto': narr,
                'bonus': f"+{bonus_val} {bonus_attr}"
            }

        if tipo_evento in ("combate", "combate_final"):
            idx = 0 if tipo_evento == "combate" else random.randint(1, len(enemigos) - 1)
            datos = enemigos[idx]
            self.enemigo_actual = Enemigo(**datos)

            # Narración de aparición
            prompt_intro = (
                "Relata en un solo fragmento de prosa la irrupción épica de "
                f"{self.enemigo_actual.nombre} ante el héroe con el contexto de {self.gestion_historia.devolver_historia()}."
            )
            intro = self.formatear_narracion(
                self.interfaz_ia.generar_texto(prompt_intro)
            )

            # Inicializamos la mecánica de combate
            self.mecanica_combate = MecanicaCombate(
                self.jugador, self.enemigo_actual
            )
            init_log = self.mecanica_combate.iniciar_mecanica_combate()
            primer_turno = "combate_jugador" if self.mecanica_combate.es_turno_jugador else "combate_enemigo"

            self.combate_activo = True
            return {
                'tipo': primer_turno,
                'intro': intro,
                'log': init_log
            }

        if tipo_evento == "final":
            prompt_final = (
                f"Escribe un epílogo evocador para la aventura de {self.jugador.nombre} en el contexto actual de {self.gestion_historia.devolver_historia()} "
                "en un solo fragmento de prosa, coherente y sin enumerar."
            )
            cierre = self.interfaz_ia.generar_texto(prompt_final)
            return {'tipo':'final','texto': self.formatear_narracion(cierre)}

        return {'tipo': tipo_evento, 'texto': ""}

    def procesar_decision_jugador(self, decision: str) -> dict:
        #self.contador_decisiones += 1 no necesario, se gestiona arriba?

        # --- COMBATE ACTIVO ---
        if self.combate_activo:
            mc = self.mecanica_combate

            # TURNO DEL JUGADOR O DEL ENEMIGO
            if mc.es_turno_jugador:
                resultado = mc.ejecutar_turno_jugador(decision)
            else:
                resultado = mc.ejecutar_turno_enemigo()

            # Si sigue en combate, devolvemos directamente
            if resultado['tipo'] in ('combate_jugador', 'combate_enemigo'):
                return resultado

            # Fin de combate, desactivamos
            self.combate_activo = False

            # Mapeos de resultados finales de combate
            if resultado['tipo'] == 'victoria':
                outro = self.formatear_narracion(
                    self.interfaz_ia.generar_texto("Narra las consecuencias de la victoria.")
                )
                # Registra la acción y persiste el estado tras la victoria
                self.gestion_historia.registrar_accion(decision, outro)
                self.persistir_estado()
                return {
                    'tipo': 'combate_victoria',
                    'log': resultado['log'],
                    'outro': outro
                }

            if resultado['tipo'] in ('huida', 'huida_enemigo'):
                who = 'jugador' if resultado['tipo'] == 'huida' else 'enemigo'
                otro_texto = (
                    f"{self.jugador.nombre} huye del combate."
                    if who == 'jugador'
                    else f"{self.enemigo_actual.nombre} huye del combate."
                )
                outro = self.formatear_narracion(
                    self.interfaz_ia.generar_texto(otro_texto)
                )
                # Registrar y persistir también la huida
                self.gestion_historia.registrar_accion(decision, outro)
                self.persistir_estado()
                return {
                    'tipo': 'combate_huido',
                    'log': resultado['log'],
                    'outro': outro
                }

            if resultado['tipo'] == 'muerte':
                outro = self.formatear_narracion(
                    self.interfaz_ia.generar_texto("Narra la muerte del protagonista.")
                )
                # Registrar y persistir la muerte
                self.gestion_historia.registrar_accion(decision, outro)
                self.eliminar_partida()
                return {'tipo': 'muerte', 'texto': outro}

        # --- FLUJO NARRATIVO / OBJETO / FINAL ---
        siguiente = self.determinar_tipo_evento()
        evento = self.iniciar_evento(siguiente)

        # Aquí debes registrar el texto que la IA ha generado para este evento
        # (sea narrativa, objeto o final) y luego persistir el estado.
        respuesta_texto = (
                evento.get('texto') or
                evento.get('intro') or
                evento.get('outro') or
                ""
        )
        self.gestion_historia.registrar_accion(decision, respuesta_texto)
        self.persistir_estado()

        return evento

    def persistir_estado(self):
        # obtenemos el resumen acumulado
        self.historia = self.gestion_historia.devolver_historia()
        datos = {
            "nombre":       self.jugador.nombre,
            "raza":         self.jugador.raza,
            "fuerza":       self.jugador.fuerza,
            "vida":         self.jugador.vida,
            "armadura":     self.jugador.armadura,
            "iniciativa":   self.jugador.iniciativa,
            "experiencia":  self.jugador.experiencia,
            "nivel":        self.jugador.nivel,
            "equipamiento": self.jugador.equipamiento,
        }
        self.dao_partidas.guardar_partida(
            self.id_usuario,
            self.jugador.nombre,
            datos,
            self.historia
        )

    def eliminar_partida(self):
        self.dao_partidas.eliminar_partida_muerte(self.id_usuario,self.jugador.nombre)
