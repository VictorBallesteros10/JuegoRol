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
        return f"Narrador: {texto}"

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
        siguiente = self.contador_decisiones + 1
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
            prompt = (
                f"Continúa la historia de {self.jugador.nombre} en {self.universo}, "
                f"centrada en {self.mision_principal}. "
                "Escribe un solo fragmento de prosa, coherente y sin enumerar, "
                "con sugerencias sutiles de acción."
            )
            frag = self.interfaz_ia.generar_texto(prompt)
            return {'tipo': 'narrativa', 'texto': self.formatear_narracion(frag)}

        if tipo_evento == "objeto":
            prompt = (
                f"Describe en un solo fragmento de prosa cómo {self.jugador.nombre} "
                "encuentra un objeto clave para la misión. Sin enumerar, solo el hallazgo."
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
            idx = 0 if tipo_evento == "combate" else -1
            datos = enemigos[idx]
            self.enemigo_actual = Enemigo(**datos)

            prompt_intro = (
                "Relata en un solo fragmento de prosa la irrupción épica de "
                f"{self.enemigo_actual.nombre} ante el héroe."
            )
            intro = self.formatear_narracion(
                self.interfaz_ia.generar_texto(prompt_intro)
            )
            self.mecanica_combate = MecanicaCombate(
                self.jugador, self.enemigo_actual
            )
            registro_iniciativa = self.mecanica_combate.iniciar_mecanica_combate()
            self.combate_activo = True
            clave = 'combate_inicio' if tipo_evento == "combate" else 'combate_final_inicio'
            return {
                'tipo': clave,
                'intro': intro,
                'init_log': registro_iniciativa
            }

        if tipo_evento == "final":
            prompt_final = (
                f"Escribe un epílogo evocador para la aventura de {self.jugador.nombre} "
                "en un solo fragmento de prosa, coherente y sin enumerar."
            )
            cierre = self.interfaz_ia.generar_texto(prompt_final)
            return {'tipo':'final','texto': self.formatear_narracion(cierre)}

        return {'tipo': tipo_evento, 'texto': ""}

    def procesar_decision_jugador(self, decision: str) -> dict:
        self.contador_decisiones += 1

        if self.combate_activo:
            if self.mecanica_combate.es_turno_jugador:
                resultado = self.mecanica_combate.ejecutar_turno_jugador(decision)
                if resultado['tipo'] == 'continuar':
                    self.mecanica_combate.es_turno_jugador = False

                    return {'tipo':'combate_jugador','log':resultado['log']}

                self.combate_activo = False
                if resultado['tipo'] == 'huida':
                    outro = self.formatear_narracion(
                        self.interfaz_ia.generar_texto(
                            f"{self.jugador.nombre} huye del combate."
                        )
                    )
                    self.gestion_historia.registrar_accion(decision, outro)
                    self._persistir_estado()
                    return {'tipo':'combate_huido','log':resultado['log'],'outro':outro}
                outro = self.formatear_narracion(
                    self.interfaz_ia.generar_texto("Narra las consecuencias de la victoria.")
                )
                self.gestion_historia.registrar_accion(decision, outro)
                self._persistir_estado()
                return {'tipo':'combate_victoria','log':resultado['log'],'outro':outro}
            else:
                resultado = self.mecanica_combate.ejecutar_turno_enemigo()
                if resultado['tipo'] == 'continuar':
                    self.mecanica_combate.es_turno_jugador = True
                    return {'tipo':'combate_enemigo','log':resultado['log']}
                # derrota
                self.combate_activo = False
                outro = self.formatear_narracion(
                    self.interfaz_ia.generar_texto("Narra la derrota del protagonista.")
                )
                self.gestion_historia.registrar_accion('turno_enemigo', outro)
                self._persistir_estado()
                return {'tipo':'combate_derrota','log':resultado['log'],'outro':outro}

        # --- FLUJO NARRATIVO / OBJETO / FINAL ---
        siguiente = self.determinar_tipo_evento()
        evento = self.iniciar_evento(siguiente)

        # registramos la acción del jugador y la respuesta de la IA
        respuesta_texto = evento.get('texto') or evento.get('intro') or evento.get('outro') or ""
        self.gestion_historia.registrar_accion(decision, respuesta_texto)
        self._persistir_estado()

        return evento

    def _persistir_estado(self):
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
