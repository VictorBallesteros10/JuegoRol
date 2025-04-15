# app/view/PlayerCreationDialog.py
import random
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox

class PlayerCreationDialog(QDialog):
    def __init__(self,game_master):
        super().__init__()
        self.setWindowTitle("Crear Personaje")
        self.game_master = game_master

        self.nombre_input = QLineEdit()
        self.raza_input = QLineEdit()

        self.fuerza_combo = QComboBox()
        self.fuerza_combo.addItems(["5 (fijo)", "Aleatoria (1-8)"])

        self.vida_combo = QComboBox()
        self.vida_combo.addItems(["13 (fijo)", "Aleatoria (8-16)"])

        self.boton_crear = QPushButton("Crear")
        self.boton_crear.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Raza:"))
        layout.addWidget(self.raza_input)
        layout.addWidget(QLabel("Fuerza:"))
        layout.addWidget(self.fuerza_combo)
        layout.addWidget(QLabel("Vida:"))
        layout.addWidget(self.vida_combo)
        layout.addWidget(self.boton_crear)

        self.setLayout(layout)

    def get_datos_personaje(self):
        nombre = self.nombre_input.text()
        raza = self.raza_input.text()
        fuerza = 5 if self.fuerza_combo.currentIndex() == 0 else random.randint(1, 8)
        vida = 13 if self.vida_combo.currentIndex() == 0 else random.randint(8, 16)

        return {
            "nombre": nombre,
            "raza": raza,
            "fuerza": fuerza,
            "vida": vida,
            "armadura": 0,
            "iniciativa": 0,
            "experiencia": 0,
            "nivel": 0,
            "equipamiento": []
        }
