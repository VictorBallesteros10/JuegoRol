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
        self.cargar_lista_partidas()

        # Botones
        boton_cargar   = QPushButton("Cargar")
        boton_nueva    = QPushButton("Nueva")
        boton_eliminar = QPushButton("Eliminar")
        boton_cancelar = QPushButton("Cancelar")

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(etiqueta)
        layout.addWidget(self.lista_partidas)

        botones = QHBoxLayout()
        botones.addWidget(boton_cargar)
        botones.addWidget(boton_nueva)
        botones.addWidget(boton_eliminar)
        botones.addWidget(boton_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        boton_cargar.clicked.connect(self.cargar_partida_en_pantalla)
        boton_nueva.clicked.connect(self.crear_partida)
        boton_eliminar.clicked.connect(self.eliminar_partida_seleccionada)
        boton_cancelar.clicked.connect(self.reject)

    def cargar_lista_partidas(self):
        self.lista_partidas.clear()
        partidas = self.administrador_bd.listar_partidas_guardadas(self.id_usuario)
        for pid, nombre, fecha in partidas:
            self.lista_partidas.addItem(f"{pid} | {nombre} ({fecha})")

    def cargar_partida_en_pantalla(self):
        item = self.lista_partidas.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Debes seleccionar una partida.")
            return
        self.id_partida = int(item.text().split(" | ")[0])
        self.accept()

    def crear_partida(self):
        self.id_partida = None
        self.accept()

    def eliminar_partida_seleccionada(self):
        item = self.lista_partidas.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Debes seleccionar una partida para eliminar.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar esta partida?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            id_partida = int(item.text().split(" | ")[0])
            exito = self.administrador_bd.eliminar_partida(id_partida)
            if exito:
                QMessageBox.information(self, "Eliminada", "Partida eliminada correctamente.")
                self.cargar_lista_partidas()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar la partida.")
