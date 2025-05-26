from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout
)
import random

class DialogoCreacionPersonaje(QDialog):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Crear Personaje")

        etiqueta_nombre = QLabel("Nombre:")
        etiqueta_raza   = QLabel("Raza:")
        etiqueta_universo = QLabel("Universo:")

        self.entrada_nombre   = QLineEdit()
        self.entrada_raza     = QComboBox()
        self.entrada_raza.addItems(["Humano","Elfo","Enano","Orco","Gnomo","Semielfo","Trasgo"])
        self.entrada_universo = QLineEdit()

        etiqueta_fuerza = QLabel("Fuerza:")
        etiqueta_vida   = QLabel("Vida:")

        self.combo_fuerza = QComboBox()
        self.combo_fuerza.addItems(["5 (fijo)","Aleatoria (1-8)"])
        self.combo_vida   = QComboBox()
        self.combo_vida.addItems(["13 (fijo)","Aleatoria (8-16)"])

        boton_crear  = QPushButton("Crear")
        boton_cancelar = QPushButton("Cancelar")

        layout = QVBoxLayout()
        layout.addWidget(etiqueta_nombre); layout.addWidget(self.entrada_nombre)
        layout.addWidget(etiqueta_universo); layout.addWidget(self.entrada_universo)
        layout.addWidget(etiqueta_raza); layout.addWidget(self.entrada_raza)
        layout.addWidget(etiqueta_fuerza); layout.addWidget(self.combo_fuerza)
        layout.addWidget(etiqueta_vida); layout.addWidget(self.combo_vida)

        botones = QHBoxLayout()
        botones.addWidget(boton_crear); botones.addWidget(boton_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        boton_crear.clicked.connect(self.accept)
        boton_cancelar.clicked.connect(self.reject)

    def obtener_datos_personaje(self) -> dict:
        nombre  = self.entrada_nombre.text().strip() or "Jugador"
        universo = self.entrada_universo.text().strip() or "Mundo de fanstasía"
        raza    = self.entrada_raza.currentText()
        fuerza  = 5 if self.combo_fuerza.currentIndex()==0 else random.randint(1,8)
        vida    = 13 if self.combo_vida.currentIndex()==0 else random.randint(8,16)
        return {
            "nombre": nombre,
            "raza": raza,
            "fuerza": fuerza,
            "vida": vida,
            "armadura": 0,
            "iniciativa": 0,
            "experiencia": 0,
            "nivel": 1,
            "equipamiento": [],
            "universo": universo
        }

    def obtener_universo(self) -> str:
        return self.entrada_universo.text().strip() or "Mundo de fanstasía"

#Esto es una locura, pero quizas pueda preguntarle primero al usuario que tipo de historia quiere y luego pasarselo a la IA para que lo tenga en cuenta a la hora de generar la historia y de generar las descripciones de los personajes y de los enemigos y los tipos de raza que puedes elegir para jugar la partida