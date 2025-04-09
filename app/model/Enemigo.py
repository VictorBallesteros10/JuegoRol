class Enemigo:

    def __init__(self, nombre, fuerza, raza, vida, armadura, iniciativa):

        self.nombre = nombre
        self.fuerza = fuerza
        self.raza = raza
        self.vida = vida
        self.armadura = armadura
        self.iniciativa = iniciativa

    def recibir_dano(self, daño_efectivo):
        self.vida -= daño_efectivo
        print(f"{self.nombre} ha recibido {daño_efectivo} puntos de daño. Vida restante: {self.vida}")

    def pasar_armadura(self,penetracion_armadura):
        if penetracion_armadura > self.armadura:
            return True
        else:
            return False

    def atacar(self,daño):
        daño_total = self.fuerza + daño
        return daño_total

