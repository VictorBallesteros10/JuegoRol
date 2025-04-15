import random
#lo cambio por creador_visual para hacerlo en una panrtalla a parte
def obtener_valor_personalizado_o_aleatorio(mensaje, fijo, aleatorio_min, aleatorio_max):
    eleccion = input(f"{mensaje} (sí/no): ").strip().lower()
    if eleccion == "sí" or eleccion == "si":
        return fijo
    else:
        return random.randint(aleatorio_min, aleatorio_max)

def crear_jugador_desde_input():
    import random

    nombre = input("Introduce tu nombre: ")

    fuerza = input("¿Quieres que tu fuerza sea 5? elige si, o tiras un dado de 8 caras para determinar tu fuerza, entonces di no (sí/no): ").strip().lower()
    fuerza = 5 if fuerza in ["sí", "si"] else random.randint(1, 8)

    raza = input("Introduce tu raza: ")

    vida = input("¿Quieres que tu vida sea 13? elige si, o tira 2 dados de 8 caras para determinar tu vida, entonces di no (sí/no): ").strip().lower()
    vida = 13 if vida in ["sí", "si"] else random.randint(8, 16)

    armadura = 0
    iniciativa = 0
    experiencia = 0
    nivel = 0
    equipamiento = []

    return {
        "nombre": nombre,
        "fuerza": fuerza,
        "raza": raza,
        "vida": vida,
        "armadura": armadura,
        "iniciativa": iniciativa,
        "experiencia": experiencia,
        "nivel": nivel,
        "equipamiento": equipamiento
    }

