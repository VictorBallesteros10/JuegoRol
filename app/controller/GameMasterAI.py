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
        if siguiente <= 1:
            return "narrativa"
        if siguiente == 3:
            return "objeto"
        if siguiente == 2:
            return "combate"
        if 4 <= siguiente <= 7:
            return "narrativa"
        if siguiente == 8:
            return "combate_final"
        return "final"

    def iniciar_evento(self, tipo_evento: str, decision: str) -> dict:
        if tipo_evento == "narrativa":
            contexto_hist = self.gestion_historia.devolver_historia()
            prompt = (
                f"El jugador escribió: «{decision}»\n\n"
                f"Continúa la historia de {self.jugador.nombre} en {self.universo}, "
                f"teniendo muy en cuenta esa decisión y el contexto histórico:\n{contexto_hist}\n\n"
                "Escribe un solo fragmento de prosa, coherente y sin enumerar, "
                "con sugerencias sutiles de acción."
            )
            frag = self.interfaz_ia.generar_texto(prompt)
            texto = self.formatear_narracion(frag)
            self.gestion_historia.registrar_accion(decision, texto)
            return {'tipo': 'narrativa', 'texto': texto}

        if tipo_evento == "objeto":
            contexto_hist = self.gestion_historia.devolver_historia()
            prompt = (
                f"El jugador escribió: «{decision}»\n\n"
                f"Describe en un solo fragmento de prosa cómo {self.jugador.nombre} encuentra un objeto clave para la misión, "
                f"considerando esa decisión y el contexto histórico:\n{contexto_hist}"
            )
            desc = self.interfaz_ia.generar_texto(prompt)
            texto = self.formatear_narracion(desc)
            bonus_attr = random.choice(['fuerza', 'vida', 'iniciativa'])
            bonus_val = random.randint(1, 3)
            setattr(self.jugador, bonus_attr, getattr(self.jugador, bonus_attr) + bonus_val)
            self.jugador.equipamiento.append(f"Objeto que otorga +{bonus_val} {bonus_attr}")
            self.gestion_historia.registrar_accion(decision, texto)
            return {
                'tipo': 'objeto',
                'texto': texto,
                'bonus': f"+{bonus_val} {bonus_attr}"
            }

        if tipo_evento in ("combate", "combate_final"):
            idx = 0 if tipo_evento == "combate" else random.randint(1, len(enemigos) - 1)
            datos = enemigos[idx]
            self.enemigo_actual = Enemigo(**datos)

            contexto_hist = self.gestion_historia.devolver_historia()
            contexto_combate = (
                f"{contexto_hist}\n"
                f"El héroe busca: {self.mision_principal}.\n"
                f"El jugador escribió: «{decision}»."
            )

            prompt_intro = (
                "Basándote en el siguiente contexto de la aventura:\n"
                f"{contexto_combate}\n\n"
                f"Describe en un fragmento de prosa la irrupción épica de {self.enemigo_actual.nombre} "
                "ante nuestro protagonista, explicando por qué bloquea su avance hacia el objetivo."
            )
            frag_intro = self.interfaz_ia.generar_texto(prompt_intro)
            intro = self.formatear_narracion(frag_intro)
            self.gestion_historia.registrar_accion(decision, intro)

            self.mecanica_combate = MecanicaCombate(self.jugador, self.enemigo_actual)
            init_log = self.mecanica_combate.iniciar_mecanica_combate()

            prompt_razon = (
                "Dado que en la aventura el héroe busca:\n"
                f"{self.mision_principal}\n"
                f"Y sabiendo que el enemigo se llama {self.enemigo_actual.nombre}, "
                "genera un único enunciado que explique por qué este enemigo bloquea el paso "
                "al héroe en este punto de la misión."
            )
            razon = self.interfaz_ia.generar_texto(prompt_razon).strip()
            init_log.insert(0, f"{self.enemigo_actual.nombre} bloquea el paso al héroe porque {razon}.")

            detalle_inicial = "\n".join(init_log)
            self.gestion_historia.registrar_accion(decision, detalle_inicial)

            primer_turno = "combate_jugador" if self.mecanica_combate.es_turno_jugador else "combate_enemigo"
            self.combate_activo = True

            return {
                'tipo': primer_turno,
                'intro': intro,
                'log': init_log
            }

        if tipo_evento == "final":
            contexto_hist = self.gestion_historia.devolver_historia()
            prompt_final = (
                f"El jugador escribió: «{decision}»\n\n"
                f"Escribe un epílogo evocador para la aventura de {self.jugador.nombre} en el contexto actual:\n"
                f"{contexto_hist}\n\n"
                "En un solo fragmento de prosa, coherente y sin enumerar."
            )
            cierre = self.interfaz_ia.generar_texto(prompt_final)
            texto = self.formatear_narracion(cierre)
            self.gestion_historia.registrar_accion(decision, texto)
            return {'tipo': 'final', 'texto': texto}

        return {'tipo': tipo_evento, 'texto': ""}

    def procesar_decision_jugador(self, decision: str) -> dict:

        if self.combate_activo:
            mc = self.mecanica_combate

            # 1) TURNO DEL JUGADOR O DEL ENEMIGO
            if mc.es_turno_jugador:
                resultado = mc.ejecutar_turno_jugador(decision)
            else:
                resultado = mc.ejecutar_turno_enemigo()

            # 2) Si el combate continúa, devolvemos directamente el diccionario con 'log' y 'tipo'
            if resultado['tipo'] in ('combate_jugador', 'combate_enemigo'):
                return resultado

            # 3) Fin de combate: desactivamos la bandera
            self.combate_activo = False

            # 4) Preparamos el detalle completo del combate (para pasarlo al prompt)
            detalle_combate = "\n".join(resultado.get('log', []))
            contexto_hist = self.gestion_historia.devolver_historia()
            objetivo = self.mision_principal

            # 5) Mapeos de resultados finales de combate

            # 5.1) VICTORIA
            if resultado['tipo'] == 'victoria':
                prompt_victoria = (
                    f"El jugador escribió: «{decision}»\n\n"
                    f"Contexto de la aventura hasta ahora:\n{contexto_hist}\n\n"
                    f"Durante el enfrentamiento con {self.enemigo_actual.nombre} sucedió:\n{detalle_combate}\n\n"
                    "El héroe ha vencido. Narra, en un solo párrafo de prosa coherente y sin enumerar, "
                    "las consecuencias inmediatas para la misión principal "
                    f"(que es: {objetivo})."
                )
                texto_victoria = self.formatear_narracion(
                    self.interfaz_ia.generar_texto(prompt_victoria)
                )
                # Registrar acción (usamos como clave la propia decision)
                self.gestion_historia.registrar_accion(decision, texto_victoria)
                self.persistir_estado()
                return {
                    'tipo': 'combate_victoria',
                    'log': resultado['log'],
                    'outro': texto_victoria
                }

            # 5.2) HUIDA (jugador o enemigo)
            if resultado['tipo'] in ('huida', 'huida_enemigo'):
                quien = 'jugador' if resultado['tipo'] == 'huida' else 'enemigo'
                razon_huida = (
                    f"{self.jugador.nombre} huye del combate."
                    if quien == 'jugador'
                    else f"{self.enemigo_actual.nombre} huye del combate."
                )
                prompt_huida = (
                    f"El jugador escribió: «{decision}»\n\n"
                    f"Contexto de la aventura hasta ahora:\n{contexto_hist}\n\n"
                    f"Durante el enfrentamiento con {self.enemigo_actual.nombre} sucedió:\n{detalle_combate}\n\n"
                    f"{razon_huida} Narra, en un solo párrafo de prosa coherente y sin enumerar, "
                    "las consecuencias de esta huida para la misión principal "
                    f"(que es: {objetivo})."
                )
                texto_huida = self.formatear_narracion(
                    self.interfaz_ia.generar_texto(prompt_huida)
                )
                self.gestion_historia.registrar_accion(decision, texto_huida)
                self.persistir_estado()
                return {
                    'tipo': 'combate_huido',
                    'log': resultado['log'],
                    'outro': texto_huida
                }

            # 5.3) MUERTE
            if resultado['tipo'] == 'muerte':
                prompt_muerte = (
                    f"El jugador escribió: «{decision}»\n\n"
                    f"Contexto de la aventura hasta ahora:\n{contexto_hist}\n\n"
                    f"Durante el enfrentamiento con {self.enemigo_actual.nombre} sucedió:\n{detalle_combate}\n\n"
                    "El protagonista muere. Narra en un solo párrafo de prosa evocadora las circunstancias "
                    "de su muerte, el impacto que tiene en la misión principal "
                    f"(que es: {objetivo}) y el legado que deja."
                )
                texto_muerte = self.formatear_narracion(
                    self.interfaz_ia.generar_texto(prompt_muerte)
                )
                self.gestion_historia.registrar_accion(decision, texto_muerte)
                self.eliminar_partida()
                return {'tipo': 'muerte', 'texto': texto_muerte}

        # 6) Si no hay combate activo, pasamos a la siguiente fase normal:
        siguiente = self.determinar_tipo_evento()
        # Observa que ahora pasamos 'decision' a iniciar_evento para que el prompt de narrativa/objeto lo incluya:
        evento = self.iniciar_evento(siguiente, decision)

        respuesta_texto = (
                evento.get('texto') or
                evento.get('intro') or
                evento.get('outro') or
                ""
        )
        # Registramos la acción del jugador (texto completo) junto con la respuesta que genera la IA
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
