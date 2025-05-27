import os
from PyQt6.QtWidgets import (
    QWidget, QTextBrowser, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QToolBar
)
from PyQt6.QtGui import QPixmap, QTextCursor, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QTimer
from app.controller.GameMasterAI import MaestroDeJuegoIA


class IUPrincipalJuego(QWidget):
    def __init__(self, maestro_juego: MaestroDeJuegoIA):
        super().__init__()
        self.maestro_juego = maestro_juego
        self.setWindowTitle("IAm the master")
        self.setGeometry(100, 100, 800, 600)
        self._init_ui()

        texto_inicial = self.maestro_juego.obtener_descripcion_entorno()
        self.iniciar_escritura(texto_inicial)

    def _init_ui(self):
        self.barra_herramientas = QToolBar()
        accion_ver_estadisticas = QAction("Ver estadísticas", self)
        accion_ver_estadisticas.triggered.connect(self.ver_estadisticas)
        accion_guardar_partida = QAction("Guardar partida", self)
        accion_guardar_partida.triggered.connect(self.guardar_partida)
        self.barra_herramientas.addAction(accion_ver_estadisticas)
        self.barra_herramientas.addAction(accion_guardar_partida)

        self.area_dialogo = QTextBrowser()
        self.area_dialogo.setReadOnly(True)
        self.area_dialogo.setStyleSheet("""
            QTextBrowser {
                background-color: #000000;
                color: #ffffff;
                padding: 8px;
            }
        """)

        self.campo_entrada = QLineEdit()
        self.campo_entrada.setPlaceholderText("Describe tu acción...")
        self.campo_entrada.returnPressed.connect(self.procesar_accion)
        self.boton_enviar = QPushButton("Enviar")
        self.boton_enviar.clicked.connect(self.procesar_accion)

        self.etiqueta_escenario = QLabel()
        self.etiqueta_escenario.setStyleSheet("border: 2px solid #ffffff;")

        self.control_audio = QAudioOutput()
        self.reproductor_audio = QMediaPlayer()
        self.reproductor_audio.setAudioOutput(self.control_audio)

        diseño_entrada = QHBoxLayout()
        diseño_entrada.addWidget(self.campo_entrada)
        diseño_entrada.addWidget(self.boton_enviar)
        diseño_principal = QVBoxLayout(self)
        diseño_principal.addWidget(self.barra_herramientas)
        diseño_principal.addWidget(self.etiqueta_escenario)
        diseño_principal.addWidget(self.area_dialogo)
        diseño_principal.addLayout(diseño_entrada)

        self.temporizador_escritura = QTimer(self)
        self.temporizador_escritura.setInterval(3)
        self.temporizador_escritura.timeout.connect(self.escribir_caracter)
        self.texto_pendiente = ""

        self.restaurar_escenario()

    def ver_estadisticas(self):
        atributos = self.maestro_juego.jugador.__dict__
        self.anexar_linea("jugador", "-- Estadísticas del jugador --")
        for clave, valor in atributos.items():
            self.anexar_linea("jugador", f"{clave}: {valor}")

    def guardar_partida(self):
        self.maestro_juego.persistir_estado()
        self.anexar_linea("jugador", "Partida guardada correctamente.")

    def procesar_accion(self):
        accion = self.campo_entrada.text().strip()
        if not accion:
            return

        self.anexar_linea("jugador", accion)
        self.campo_entrada.clear()

        resultado = self.maestro_juego.procesar_decision_jugador(accion)
        texto_respuesta = self.obtener_texto(resultado)
        if texto_respuesta:
            self.iniciar_escritura(texto_respuesta)

        if resultado.get('tipo') == 'combate_enemigo':
            mc = self.maestro_juego.mecanica_combate
            turno_enemigo = mc.ejecutar_turno_enemigo()
            bloque = "\n".join(turno_enemigo['log'])
            if mc.es_turno_jugador:
                bloque += "\nAhora es tu turno: escribe tu acción."
            self.iniciar_escritura(bloque)

    def obtener_texto(self, resultado: dict) -> str:
        tipo = resultado.get('tipo', '')

        if tipo == 'narrativa':
            self.restaurar_escenario()
            return resultado['texto']
        if tipo == 'objeto':
            self.restaurar_escenario()
            return f"{resultado['texto']}\nBonus: {resultado['bonus']}"

        if tipo in ('combate_jugador', 'combate_enemigo'):
            if 'intro' in resultado:
                self.mostrar_orco()
                self.anexar_linea("narrador", resultado['intro'])
            for linea in resultado['log']:
                self.anexar_linea("narrador", linea)
            if tipo == 'combate_jugador':
                return "\nAhora es tu turno: escribe tu acción."
            return ""

        if tipo == 'combate_victoria':
            self.restaurar_escenario()
            return "\n".join(resultado['log']) + "\n" + resultado.get('outro', '')
        if tipo == 'combate_huido':
            self.restaurar_escenario()
            return "\n".join(resultado['log']) + "\n" + resultado.get('outro', '')
        if tipo == 'muerte':
            self.mostrar_muerte(resultado.get('texto', ''))
            return resultado.get('texto', '')

        if tipo == 'final':
            self.restaurar_escenario()
            return resultado['texto']

        return ""

    def anexar_linea(self, emisor: str, texto: str):
        color = "#00FFFF" if emisor == "jugador" else "#ffffff"
        estilo = "italic" if emisor == "jugador" else "normal"
        etiqueta = "Jugador" if emisor == "jugador" else "Narrador"
        html = f'<p><b style="color:{color}; font-style:{estilo};">{etiqueta}:</b> {texto}</p>'
        self.area_dialogo.append(html)
        self.desplazar_auto()

    def iniciar_escritura(self, texto: str):
        self.texto_pendiente = texto
        self.area_dialogo.append('<p><b style="color:#ffffff;">Narrador:</b> ')
        self.area_dialogo.moveCursor(QTextCursor.MoveOperation.End)
        self.temporizador_escritura.start()

    def escribir_caracter(self):
        if not self.texto_pendiente:
            self.temporizador_escritura.stop()
            return
        caracter = self.texto_pendiente[0]
        self.texto_pendiente = self.texto_pendiente[1:]
        cursor = self.area_dialogo.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(caracter)
        self.desplazar_auto()

    def desplazar_auto(self):
        barra = self.area_dialogo.verticalScrollBar()
        barra.setValue(barra.maximum())

    def restaurar_escenario(self):
        carpeta = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archivos'))
        self.cambiar_medios(
            os.path.join(carpeta, 'bosque.jpg'),
            os.path.join(carpeta, 'musica_ambiente2.mp3')
        )

    def mostrar_orco(self):
        carpeta = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archivos'))
        self.cambiar_medios(
            os.path.join(carpeta, 'orco.jpg'),
            os.path.join(carpeta, 'musica_ambiente.mp3')
        )

    def mostrar_arte_combate(self):
        carpeta = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archivos'))
        self.cambiar_medios(
            os.path.join(carpeta, 'rocadragon.png'),
            os.path.join(carpeta, 'musica_ambiente.mp3')
        )

    def cambiar_medios(self, ruta_imagen: str, ruta_musica: str):
        imagen = QPixmap(ruta_imagen).scaledToWidth(600)
        self.etiqueta_escenario.setPixmap(imagen)
        self.reproductor_audio.setSource(QUrl.fromLocalFile(ruta_musica))
        self.reproductor_audio.play()

    def mostrar_muerte(self, mensaje_final: str):
        self.temporizador_escritura.stop()
        self.campo_entrada.setDisabled(True)
        self.boton_enviar.setDisabled(True)
        self.anexar_linea("narrador", mensaje_final)
