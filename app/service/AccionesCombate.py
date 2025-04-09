import random

class AccionesCombate:

    def __init__(self, jugador, enemigo):
        self.jugador = jugador
        self.enemigo = enemigo

    def turno_jugador(self):
        print(f"{self.jugador.nombre} es tu turno, elige un movimiento: ")

        while True:
            eleccion = input("atacar o huir: ").lower()
            if eleccion == "atacar":
                self.atacar(self.jugador, self.enemigo)
                break
            elif eleccion == "huir":
                if self.huir(self.jugador):
                    print(f"{self.jugador.nombre} ha huido del combate.")
                    return True
                break
            else:
                print("Opción no válida. Elige 'atacar' o 'huir'.")

        return False

    def turno_enemigo(self):
        print(f"{self.enemigo.nombre} tiene turno:")
        # Aquí la IA del enemigo decide qué hacer
        eleccion = random.choice(["atacar", "huir"])#este ramdon hay que quitarlo, la ia debe gestionarlo

        if eleccion == "atacar":
            self.atacar(self.enemigo, self.jugador)
        elif eleccion == "huir":
            self.huir()
            if self.huir(self.enemigo):
                print(f"{self.enemigo.nombre} ha huido del combate.")
                return True

        return False

    def iniciar_combate(self):
        huir = False
        iniciativaJugador = self.generar_iniciativa() + self.jugador.iniciativa
        print(f"{self.jugador.nombre} tienes {iniciativaJugador} de iniciativa.")
        iniciativaEnemigo = self.generar_iniciativa() + self.enemigo.iniciativa
        print(f"{self.enemigo.nombre} tiene {iniciativaEnemigo} de iniciativa.")

        if iniciativaJugador >= iniciativaEnemigo:
            print("Comienzas atacando")
        else:
            print("El enemigo comienza atacando")

        while self.jugador.vida > 0 and self.enemigo.vida > 0 and not huir:
            if iniciativaJugador >= iniciativaEnemigo:
                huir = self.turno_jugador()
                if self.enemigo.vida <= 0:
                    print(f"{self.enemigo.nombre} ha sido derrotado.")
                    break
                if huir:
                    break
                huir = self.turno_enemigo()
                if self.jugador.vida <= 0:
                    print(f"{self.jugador.nombre} has sido derrotado.")
                    break
            else:
                huir = self.turno_enemigo()
                if self.jugador.vida <= 0:
                    print(f"{self.jugador.nombre} has sido derrotado.")
                    break
                if huir:
                    break
                huir = self.turno_jugador()
                if self.enemigo.vida <= 0:
                    print(f"{self.enemigo.nombre} ha sido derrotado.")
                    break

    def atacar(self, atacante, objetivo):
        print(f"{atacante.nombre} ataca a {objetivo.nombre}.")
        print("Tirada de dado para atravesar la armadura (0-20):")
        pasarArmadura = random.randint(0, 20)
        print(f"Tirada: {pasarArmadura}")

        if objetivo.pasar_armadura(pasarArmadura):
            print(f"¡La armadura ha sido superada! Tirada de dado de 6 caras + fuerza de {atacante.fuerza}.")
            daño = random.randint(0, 6) + atacante.fuerza
            print(f"El ataque inflige {daño} puntos de daño.")
            objetivo.recibir_dano(daño)
        else:
            print(f"El ataque de {atacante.nombre} fue bloqueado por la armadura de {objetivo.nombre}.")

    def huir(self, personaje):
        tiradaHuir = random.randint(0, 20)
        if tiradaHuir > 15:
            print(f"{personaje.nombre} huye con éxito.")
            return True
        print(f"{personaje.nombre} no ha logrado huir.")
        return False

    def generar_iniciativa(self):
        iniciativa = random.randint(0, 20)
        print("Tirada de dado para iniciativa (0-20):")
        print(f"La tirada fue: {iniciativa}")
        return iniciativa
