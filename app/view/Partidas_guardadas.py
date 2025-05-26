from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QHBoxLayout, QMessageBox
)
from app.service.GestorBBDD import AdministradorBaseDatosSA

class DialogoPartidasGuardadas(QDialog):
    def __init__(self, id_usuario: int, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Partidas Guardadas")
        self.administrador_bd = AdministradorBaseDatosSA()
        self.id_usuario       = id_usuario
        self.id_partida       = None

        etiqueta = QLabel("Selecciona una partida:")
        self.lista_partidas = QListWidget()
        partidas = self.administrador_bd.listar_partidas_guardadas(id_usuario)
        for pid, nombre, fecha in partidas:
            self.lista_partidas.addItem(f"{pid} | {nombre} ({fecha})")

        boton_cargar = QPushButton("Cargar")
        boton_nueva  = QPushButton("Nueva")
        boton_cancelar = QPushButton("Cancelar")

        layout = QVBoxLayout()
        layout.addWidget(etiqueta)
        layout.addWidget(self.lista_partidas)

        botones = QHBoxLayout()
        botones.addWidget(boton_cargar)
        botones.addWidget(boton_nueva)
        botones.addWidget(boton_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        boton_cargar.clicked.connect(self._cargar_partida)
        boton_nueva.clicked.connect(self._crear_partida)
        boton_cancelar.clicked.connect(self.reject)

    def _cargar_partida(self):
        item = self.lista_partidas.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Debes seleccionar una partida.")
            return
        self.id_partida = int(item.text().split(" | ")[0])
        self.accept()

    def _crear_partida(self):
        self.id_partida = None
        self.accept()
