import random

class MecanicaCombate:
    def __init__(self, jugador, enemigo):
        self.jugador = jugador
        self.enemigo = enemigo
        self.es_turno_jugador = False

    def generar_iniciativa(self) -> int:
        return random.randint(1, 20)

    def iniciar_mecanica_combate(self) -> list[str]:
        registro = []
        ini_j = self.generar_iniciativa() + self.jugador.iniciativa
        ini_e = self.generar_iniciativa() + self.enemigo.iniciativa
        registro.append(f"{self.jugador.nombre} tiene iniciativa {ini_j}.")
        registro.append(f"{self.enemigo.nombre} tiene iniciativa {ini_e}.")
        if ini_j >= ini_e:
            registro.append("Comienza el jugador.")
            self.es_turno_jugador = True
        else:
            registro.append("Comienza el enemigo.")
            self.es_turno_jugador = False
        return registro

    def ejecutar_turno_jugador(self, decision: str) -> dict:
        registro = []

        if self.jugador.vida <= 0:
            return {"tipo": "muerte", "log": ["Has muerto."]}

        decision = decision.strip().lower()
        if decision in ("huir", "escapar"):
            huido, msg = self._intentar_huir(self.jugador)
            registro.append(msg)
            if huido:
                return {"tipo": "huida", "log": registro}
            # huida fallida, cede turno
            self.es_turno_jugador = False
            return {"tipo": "combate_enemigo", "log": registro}

        _, sublog = self._realizar_ataque(self.jugador, self.enemigo)
        registro.extend(sublog)
        if self.enemigo.vida <= 0:
            return {"tipo": "victoria", "log": registro}

        self.es_turno_jugador = False
        return {"tipo": "combate_enemigo", "log": registro}

    def ejecutar_turno_enemigo(self) -> dict:
        registro = []

        # Si el jugador ya no tiene vida -> muerte
        if self.jugador.vida <= 0:
            return {"tipo": "muerte", "log": ["El enemigo te remata. Has muerto."]}

        # Si la vida del enemigo es baja, intenta huir
        if self.enemigo.vida <= 3:
            huido, msg = self._intentar_huir(self.enemigo)
            registro.append(msg)
            if huido:
                return {"tipo": "huida_enemigo", "log": registro}
            else:
                self.es_turno_jugador = True
                return {"tipo": "combate_jugador", "log": registro}

        _, sublog = self._realizar_ataque(self.enemigo, self.jugador)
        registro.extend(sublog)

        if self.jugador.vida <= 0:
            return {"tipo": "muerte", "log": ["Has muerto."]}

        self.es_turno_jugador = True
        return {"tipo": "combate_jugador", "log": registro}

    def _realizar_ataque(self, atk, defn):
        log = [f"{atk.nombre} ataca a {defn.nombre}"]
        tirada = random.randint(1, 20)
        log.append(f"Tirada de armadura: {tirada}")
        if defn.pasar_armadura(tirada):
            dano = random.randint(1, 6) + atk.fuerza
            defn.recibir_dano(dano)
            log.append(f"Inflige {dano} de daño. {defn.nombre}.vida={defn.vida}")
        else:
            log.append("El ataque fue bloqueado.")
        return False, log

    def _intentar_huir(self, personaje):
        tir = random.randint(1, 20)
        if tir > 15:
            return True, f"{personaje.nombre} huye con éxito."
        return False, f"{personaje.nombre} no logra huir."
