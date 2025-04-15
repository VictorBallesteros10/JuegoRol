# app/view/CombatDialog.py
import os
import random
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl


#no me pone la descripcion de la pelea en ningun lado, ni me dice si he ganado o perdido o huido antes de cerrarse
class CombateDialog(QDialog):
    def __init__(self, jugador, enemigo):
        super().__init__()
        self.jugador = jugador
        self.enemigo = enemigo
        self.resultado_final = None  # "victoria", "derrota" o "huida"
        self.init_ui()
        self.iniciar_musica()

    def init_ui(self):
        self.setWindowTitle("Combate")
        self.setMinimumSize(600, 400)

        # Layout principal
        self.layout = QVBoxLayout()

        # Imagen representativa del combate
        ruta_imagen = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "archivos", "rocadragon.png"))
        self.imagen_label = QLabel()
        self.imagen_label.setPixmap(QPixmap(ruta_imagen).scaledToWidth(400))
        self.layout.addWidget(self.imagen_label)

        # Área de log para mostrar el desarrollo del combate
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Registro de combate...")
        self.layout.addWidget(self.log_text)

        # Botones para acciones: Atacar y Huir
        btn_layout = QHBoxLayout()
        self.btn_atacar = QPushButton("Atacar")
        self.btn_huir = QPushButton("Huir")
        btn_layout.addWidget(self.btn_atacar)
        btn_layout.addWidget(self.btn_huir)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

        # Conectar los botones con sus funciones
        self.btn_atacar.clicked.connect(self.accion_atacar)
        self.btn_huir.clicked.connect(self.accion_huir)

        # Preparar reproductor de música
        self.audio_output = QAudioOutput()
        self.music_player = QMediaPlayer()
        self.music_player.setAudioOutput(self.audio_output)

    def iniciar_musica(self):
        """Reproduce la música de fondo del combate."""
        ruta_musica = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "archivos", "musica_ambiente.mp3"))
        self.music_player.setSource(QUrl.fromLocalFile(ruta_musica))
        self.music_player.play()

    def log(self, mensaje):
        """Agrega un mensaje al registro del combate."""
        contenido = self.log_text.toPlainText()
        self.log_text.setPlainText(contenido + "\n" + mensaje)

    def accion_atacar(self):
        """Simula el turno del jugador al atacar y, a continuación, el turno del enemigo."""
        # Turno del jugador:
        self.log(f"{self.jugador.nombre} ataca a {self.enemigo.nombre}.")
        tirada = random.randint(1, 20)
        self.log(f"Tirada para atravesar la armadura: {tirada}")

        if self.enemigo.pasar_armadura(tirada):
            daño = random.randint(1, 6) + self.jugador.fuerza
            self.log(f"¡Ataque exitoso! Daño infligido: {daño}")
            self.enemigo.recibir_dano(daño)
        else:
            self.log(f"El ataque fue bloqueado por la armadura de {self.enemigo.nombre}.")

        # Verificar si el enemigo fue derrotado:
        if self.enemigo.vida <= 0:
            self.log(f"{self.enemigo.nombre} ha sido derrotado.")
            self.resultado_final = "victoria"
            self.music_player.stop()
            self.accept()  # Cierra el diálogo y devuelve el resultado
            return

        # Si el combate sigue, el enemigo ataca:
        self.turno_enemigo()

    def turno_enemigo(self):
        """Simula el turno del enemigo y actualiza el combate."""
        self.log(f"{self.enemigo.nombre} ataca a {self.jugador.nombre}.")
        tirada = random.randint(1, 20)
        self.log(f"Tirada para atravesar la armadura: {tirada}")

        if self.jugador.pasar_armadura(tirada):
            daño = random.randint(1, 6) + self.enemigo.fuerza
            self.log(f"El enemigo inflige {daño} puntos de daño.")
            self.jugador.recibir_dano(daño)
        else:
            self.log("El ataque del enemigo fue bloqueado.")

        # Verificar si el jugador fue derrotado:
        if self.jugador.vida <= 0:
            self.log(f"{self.jugador.nombre} ha sido derrotado.")
            self.resultado_final = "derrota"
            self.music_player.stop()
            self.accept()

    def accion_huir(self):
        """Simula que el jugador intenta huir del combate."""
        tirada = random.randint(1, 20)
        self.log(f"Tirada para huir: {tirada}")
        if tirada > 15:
            self.log(f"{self.jugador.nombre} huye con éxito.")
            self.resultado_final = "huida"
            self.music_player.stop()
            self.accept()
        else:
            self.log(f"{self.jugador.nombre} no logra huir.")
            # Si huir falla, el enemigo tiene su turno:
            self.turno_enemigo()

    def get_resultado(self):
        """Devuelve el resultado final del combate."""
        return self.resultado_final
