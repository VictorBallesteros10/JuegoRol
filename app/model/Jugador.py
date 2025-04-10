
class Jugador:
    def __init__(self, nombre, fuerza, raza, vida, armadura, equipamiento, iniciativa, experiencia, nivel):

        self.nombre = nombre
        self.fuerza = fuerza
        self.raza = raza
        self.vida = vida
        self.armadura = armadura
        self.equipamiento = equipamiento
        self.iniciativa = iniciativa
        self.experiencia=experiencia
        self.nivel=nivel

    def recibir_dano(self, daño_efectivo):
        self.vida -= daño_efectivo
        print(f"{self.nombre} ha recibido {daño_efectivo} puntos de daño. Vida restante: {self.vida}")

    def pasar_armadura(self,penetracion_armadura):
        if penetracion_armadura > self.armadura:
            return True
        else:
            return False

    def equipar_armadura(self, nueva_armadura):
        self.armadura = nueva_armadura
        print(f"{self.nombre} ha equipado una nueva armadura de nivel {self.armadura}.")

    def atacar(self,daño):
        daño_total = self.fuerza + daño
        return daño_total

    def morir(self):
        if self.vida <= 0:
            return "Estas muerto"

    def comprobar_experiencia(self):
        if self.experiencia >= 100: self.experiencia=-100 and self.subir_nivel()


    def subir_nivel(self):
        self.nivel=+1
        self.iniciativa=+1
        self.vida=+3
        self.fuerza=+3

    def mostrar_equipo(self):
        print("Equipamiento actual:")
        for objeto in self.equipamiento:
            print(f"- {objeto}")

    def mostrar_estado(self):
        print(f"Jugador: {self.nombre}")
        print(f"Raza: {self.raza}")
        print(f"Vida: {self.vida}")
        print(f"Fuerza: {self.fuerza}")
        print(f"Armadura: {self.armadura}")
        print(f"Iniciativa: {self.iniciativa}")
        print(f"Experiencia: {self.experiencia}")
        print(f"Nivel: {self.nivel}")
        print(self.equipamiento)
        print("-" * 30)
