import os
import requests
from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

class GameUI(QWidget):
    def __init__(self, game_master):
        super().__init__()
        self.game_master = game_master
        self.setWindowTitle("IAm the rol")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.iniciar_juego()

    def init_ui(self):
        self.story_text = QTextEdit()
        self.story_text.setReadOnly(True)
        self.story_text.setPlaceholderText("Aquí se muestra la historia...")

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Escribe tu acción aquí...")
        self.input_line.returnPressed.connect(self.process_input)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.process_input)

        ruta_imagen = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "archivos", "bosque.jpg"))
        self.scene_image = QLabel()
        self.scene_image.setPixmap(QPixmap(ruta_imagen).scaledToWidth(600))
        self.scene_image.setStyleSheet("border: 2px solid black;")

        self.audio_output = QAudioOutput()
        self.music_player = QMediaPlayer()
        self.music_player.setAudioOutput(self.audio_output)
        self.play_music(os.path.join(os.path.dirname(__file__), "..", "archivos", "musica_ambiente2.mp3"))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scene_image)
        main_layout.addWidget(self.story_text)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def iniciar_juego(self):
        introduccion= self.game_master.describir_entorno()
        self.añadir_texto_juego(introduccion)
        print(f"{introduccion}--------juego iniciado")

    def añadir_texto_juego(self, text):
        self.story_text.append(text)

    def process_input(self):
        texto_usuario = self.input_line.text().strip()
        if not texto_usuario:
            return
        self.añadir_texto_juego(f"\nElegiste: {texto_usuario} \n")
        self.input_line.clear()
        respuesta = self.game_master.resolver_decision_jugador(texto_usuario)
        self.añadir_texto_juego(respuesta)
        #self.play_music(os.path.join(os.path.dirname(__file__), "..", "archivos", "musica_ambiente2.mp3")) si hago esto cambia la musica
        #self.set_scene_image(os.path.join(os.path.dirname(__file__), "..", "archivos", "rocadragon.png"))

    def play_music(self, filename):
        ruta_musica = os.path.abspath(filename)
        self.music_player.setSource(QUrl.fromLocalFile(ruta_musica))
        self.music_player.play()

    def set_scene_image(self, filename):
        ruta_imagen = os.path.abspath(filename)
        self.scene_image.setPixmap(QPixmap(ruta_imagen).scaledToWidth(600))
