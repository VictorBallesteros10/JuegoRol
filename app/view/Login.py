from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox
)
from sqlalchemy.exc import IntegrityError
from app.service.GestorBBDD import AdministradorBaseDatosSA

class DialogoInicioSesion(QDialog):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Iniciar Sesión")
        self.administrador_bd = AdministradorBaseDatosSA()
        self.id_usuario = None

        etiqueta_usuario = QLabel("Usuario:")
        etiqueta_clave   = QLabel("Contraseña:")
        self.entrada_usuario = QLineEdit()
        self.entrada_usuario.setPlaceholderText("Nombre de usuario")
        self.entrada_clave = QLineEdit()
        self.entrada_clave.setPlaceholderText("Contraseña")
        self.entrada_clave.setEchoMode(QLineEdit.EchoMode.Password)

        boton_entrar    = QPushButton("Entrar")
        boton_registrar = QPushButton("Registrar")
        boton_cancelar  = QPushButton("Cancelar")

        layout = QVBoxLayout()
        layout.addWidget(etiqueta_usuario)
        layout.addWidget(self.entrada_usuario)
        layout.addWidget(etiqueta_clave)
        layout.addWidget(self.entrada_clave)

        botones = QHBoxLayout()
        botones.addWidget(boton_entrar)
        botones.addWidget(boton_registrar)
        botones.addWidget(boton_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        boton_entrar.clicked.connect(self._iniciar_sesion)
        boton_registrar.clicked.connect(self._registrar_usuario)
        boton_cancelar.clicked.connect(self.reject)

    def _iniciar_sesion(self):
        usuario = self.entrada_usuario.text().strip()
        clave   = self.entrada_clave.text().strip()
        if not usuario or not clave:
            QMessageBox.warning(self, "Error", "Debes completar ambos campos.")
            return
        uid = self.administrador_bd.verificar_usuario(usuario, clave)
        if uid:
            self.id_usuario = uid
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")

    def _registrar_usuario(self):
        usuario = self.entrada_usuario.text().strip()
        clave   = self.entrada_clave.text().strip()
        if not usuario or not clave:
            QMessageBox.warning(self, "Error", "Debes completar ambos campos.")
            return
        try:
            uid = self.administrador_bd.crear_usuario(usuario, clave)
            QMessageBox.information(self, "Éxito", "Usuario registrado.")
            self.id_usuario = uid
            self.accept()
        except IntegrityError:
            QMessageBox.warning(self, "Error", "El usuario ya existe.")
