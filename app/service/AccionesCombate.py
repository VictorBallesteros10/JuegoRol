# app/service/AccionesCombate.py

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
        ini_jugador = self.generar_iniciativa() + self.jugador.iniciativa
        ini_enemigo = self.generar_iniciativa() + self.enemigo.iniciativa
        registro.append(f"{self.jugador.nombre} tiene iniciativa {ini_jugador}.")
        registro.append(f"{self.enemigo.nombre} tiene iniciativa {ini_enemigo}.")
        if ini_jugador >= ini_enemigo:
            registro.append("Comienza el jugador.")
            self.es_turno_jugador = True
        else:
            registro.append("Comienza el enemigo.")
            self.es_turno_jugador = False
        return registro

    def ejecutar_turno_jugador(self, decision: str) -> dict:
        registro = []

        if self.jugador.vida <= 0:
            return {
                "tipo": "muerte",
                "log": ["Tus heridas son mortales. El mundo se desvanece mientras caes. Has muerto."],
            }

        decision = decision.strip().lower()
        if decision in ("huir", "escapar"):
            huido, mensaje = self._intentar_huir(self.jugador)
            registro.append(mensaje)
            if huido:
                return {'tipo': 'huida', 'log': registro}
            else:
                # Falló la huida: pierde turno
                self.es_turno_jugador = False
                return {'tipo': 'continuar', 'log': registro}

        # Decide atacar
        _, subregistro = self._realizar_ataque(self.jugador, self.enemigo)
        registro.extend(subregistro)
        if self.enemigo.vida <= 0:
            return {'tipo': 'victoria', 'log': registro}
        # Tras atacar, cede el turno
        self.es_turno_jugador = False
        return {'tipo': 'continuar', 'log': registro}

    def ejecutar_turno_enemigo(self) -> dict:
        registro = []

        # Si el jugador ya está muerto, termina inmediatamente
        if self.jugador.vida <= 0:
            return {'tipo': 'derrota', 'log': ["El jugador no tiene vida y cae derrotado."]}

        # Si la vida del enemigo es baja, intenta huir
        if self.enemigo.vida <= 3:
            huido, mensaje = self._intentar_huir(self.enemigo)
            registro.append(mensaje)  # siempre registramos el mensaje
            if huido:
                return {'tipo': 'huida_enemigo', 'log': registro}
            else:
                # huida fallida: fin de turno, vuelve al jugador
                return {'tipo': 'continuar', 'log': registro}

        # Si no entra en huida, ataca
        _, subregistro = self._realizar_ataque(self.enemigo, self.jugador)
        registro.extend(subregistro)

        if self.jugador.vida <= 0:
            return {'tipo': 'derrota', 'log': registro}
        # Tras atacar, pasa el turno al jugador
        self.es_turno_jugador = True
        return {'tipo': 'continuar', 'log': registro}

    def _realizar_ataque(self, atacante, defensor):
        registro = [f"{atacante.nombre} ataca a {defensor.nombre}"]
        tirada = random.randint(1, 20)
        registro.append(f"Tirada de armadura: {tirada}")
        if defensor.pasar_armadura(tirada):
            daño = random.randint(1, 6) + atacante.fuerza
            defensor.recibir_dano(daño)
            registro.append(f"Inflige {daño} de daño. Vida {defensor.nombre}={defensor.vida}")
        else:
            registro.append("El ataque fue bloqueado.")
        return False, registro

    def _intentar_huir(self, personaje):
        tirada = random.randint(1, 20)
        if tirada > 15:
            return True, f"{personaje.nombre} huye con éxito."
        else:
            return False, f"{personaje.nombre} no logra huir."
