import os
from PyQt6.QtWidgets import (
    QWidget, QTextBrowser, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QToolBar, QInputDialog
)
from PyQt6.QtTextToSpeech import QTextToSpeech
from PyQt6.QtGui import QPixmap, QTextCursor, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QTimer
from app.controller.GameMasterAI import MaestroDeJuegoIA


class IUPrincipalJuego(QWidget):
    def __init__(self, maestro_juego: MaestroDeJuegoIA):
        super().__init__()
        self.maestro_juego = maestro_juego
        self.is_reading = False
        self.setWindowTitle("IAm the master")
        self.setGeometry(100, 100, 800, 600)
        self._init_ui()

        texto_inicial = self.maestro_juego.obtener_descripcion_entorno()
        self.iniciar_escritura(texto_inicial)

    def _init_ui(self):
        self.barra_herramientas = QToolBar()

        # Acciones básicas
        accion_ver_estadisticas = QAction("Ver estadísticas", self)
        accion_ver_estadisticas.triggered.connect(self.ver_estadisticas)
        accion_guardar_partida = QAction("Guardar partida", self)
        accion_guardar_partida.triggered.connect(self.guardar_partida)

        # Menú Configuración
        accion_configurar_velocidad = QAction("Velocidad de escritura", self)
        accion_configurar_velocidad.triggered.connect(self.configurar_velocidad)

        accion_configurar_voz = QAction("Cambiar voz del narrador", self)
        accion_configurar_voz.triggered.connect(self.configurar_voz)

        # Pitch
        accion_pitch_up = QAction("tono +", self)
        accion_pitch_up.triggered.connect(self.pitch_up)
        accion_pitch_down = QAction("tono -", self)
        accion_pitch_down.triggered.connect(self.pitch_down)

        # Volumen audio
        accion_vol_audio_up = QAction("Vol. Audio +", self)
        accion_vol_audio_up.triggered.connect(self.vol_audio_up)
        accion_vol_audio_down = QAction("Vol. Audio -", self)
        accion_vol_audio_down.triggered.connect(self.vol_audio_down)

        # Volumen TTS
        accion_vol_tts_up = QAction("Vol. TTS +", self)
        accion_vol_tts_up.triggered.connect(self.vol_tts_up)
        accion_vol_tts_down = QAction("Vol. TTS -", self)
        accion_vol_tts_down.triggered.connect(self.vol_tts_down)

        # Añadir acciones
        for accion in [accion_ver_estadisticas, accion_guardar_partida,
                       accion_configurar_velocidad, accion_configurar_voz,
                       accion_pitch_up, accion_pitch_down,
                       accion_vol_audio_up, accion_vol_audio_down,
                       accion_vol_tts_up, accion_vol_tts_down]:
            self.barra_herramientas.addAction(accion)
        self.barra_herramientas.addSeparator()

        # Área de diálogo
        self.area_dialogo = QTextBrowser()
        self.area_dialogo.setReadOnly(True)
        self.area_dialogo.setStyleSheet("""
            QTextBrowser {
                background-color: #000000;
                color: #ffffff;
                padding: 8px;
            }
        """)

        # Entrada y botón
        self.campo_entrada = QLineEdit()
        self.campo_entrada.setPlaceholderText("Describe tu acción...")
        self.campo_entrada.returnPressed.connect(self.procesar_accion)
        self.boton_enviar = QPushButton("Enviar")
        self.boton_enviar.clicked.connect(self.procesar_accion)

        # Escenario imagen + audio
        self.etiqueta_escenario = QLabel()
        self.etiqueta_escenario.setStyleSheet("border: 2px solid #ffffff;")
        self.control_audio = QAudioOutput()
        self.reproductor_audio = QMediaPlayer()
        self.reproductor_audio.setAudioOutput(self.control_audio)
        self.control_audio.setVolume(0.5)

        # Inicializar TTS
        self.stt = QTextToSpeech()
        self.stt.stateChanged.connect(self._tts_state_changed)
        self.voices = list(self.stt.availableVoices())
        self.voice_index = 0
        if self.voices:
            self.stt.setVoice(self.voices[self.voice_index])
        self.stt.setRate(0.0)
        self.stt.setPitch(0.0)
        self.stt.setVolume(0.5)

        # Temporizador escritura
        self.temporizador_escritura = QTimer(self)
        self.velocidad_escritura = 3
        self.temporizador_escritura.setInterval(self.velocidad_escritura)
        self.temporizador_escritura.timeout.connect(self.escribir_caracter)
        self.texto_pendiente = ""

        # Layouts
        diseño_entrada = QHBoxLayout()
        diseño_entrada.addWidget(self.campo_entrada)
        diseño_entrada.addWidget(self.boton_enviar)
        diseño_principal = QVBoxLayout(self)
        diseño_principal.addWidget(self.barra_herramientas)
        diseño_principal.addWidget(self.etiqueta_escenario)
        diseño_principal.addWidget(self.area_dialogo)
        diseño_principal.addLayout(diseño_entrada)

        self.restaurar_escenario()

    def _tts_state_changed(self, state):
        from PyQt6.QtTextToSpeech import QTextToSpeech
        if state == QTextToSpeech.State.Ready:
            self.is_reading = False
        else:
            self.is_reading = True

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
        estilo_etiqueta = f'<p><b style="color:{color}; font-style:{estilo};">{etiqueta}:</b> {texto}</p>'
        self.area_dialogo.append(estilo_etiqueta)
        self.desplazar_auto()
        if emisor != "jugador" and not self.is_reading:
            self.stt.say(texto)

    def iniciar_escritura(self, texto: str):
        self.texto_pendiente = texto
        self.area_dialogo.append('<p><b style="color:#ffffff;">Narrador:</b> ')
        self.area_dialogo.moveCursor(QTextCursor.MoveOperation.End)
        if not self.is_reading:
            self.stt.say(texto)
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
            os.path.join(carpeta, 'orco.png'),
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

    # Configuración dinámica
    def configurar_velocidad(self):
        valor, ok = QInputDialog.getInt(
            self, "Configurar velocidad", "Intervalo en milisegundos (menos = más rápido):",
            value=self.velocidad_escritura, min=1, max=100)
        if ok:
            self.velocidad_escritura = valor
            self.temporizador_escritura.setInterval(valor)
            self.anexar_linea("jugador", f"Velocidad de escritura ajustada a {valor} ms por carácter.")

    def configurar_voz(self):
        if not self.voices:
            self.anexar_linea("jugador", "No hay voces disponibles.")
            return
        opciones = [f"Voz {i+1} - {voz.name()}" for i,voz in enumerate(self.voices)]
        selec, ok = QInputDialog.getItem(
            self, "Seleccionar voz", "Elige una voz:", opciones, current=0, editable=False)
        if ok:
            idx = opciones.index(selec)
            self.voice_index = idx
            self.stt.setVoice(self.voices[idx])
            self.anexar_linea("jugador", f"Voz del narrador cambiada a: {selec}")
            if not self.is_reading:
                self.stt.say("¡HOLA VIAJERO!")

    def pitch_up(self):
        nuevo = min(2.0, self.stt.pitch() + 0.1)
        self.stt.setPitch(nuevo)
        self.anexar_linea("jugador", f"tono ajustado a {nuevo:.1f}")
        if not self.is_reading:
            self.stt.say("¡HOLA VIAJERO!")

    def pitch_down(self):
        nuevo = max(-2.0, self.stt.pitch() - 0.1)
        self.stt.setPitch(nuevo)
        self.anexar_linea("jugador", f"tono ajustado a {nuevo:.1f}")
        if not self.is_reading:
            self.stt.say("¡HOLA VIAJERO!")

    def vol_audio_up(self):
        actual = self.control_audio.volume()
        nuevo = min(1.0, actual + 0.1)
        self.control_audio.setVolume(nuevo)
        self.anexar_linea("jugador", f"Volumen de audio ajustado a {nuevo*100:.0f}%")

    def vol_audio_down(self):
        actual = self.control_audio.volume()
        nuevo = max(0.0, actual - 0.1)
        self.control_audio.setVolume(nuevo)
        self.anexar_linea("jugador", f"Volumen de audio ajustado a {nuevo*100:.0f}%")

    def vol_tts_up(self):
        actual = self.stt.volume()
        nuevo = min(1.0, actual + 0.1)
        self.stt.setVolume(nuevo)
        self.anexar_linea("jugador", f"Volumen de narrador ajustado a {nuevo*100:.0f}%")
        if not self.is_reading:
            self.stt.say("¡HOLA VIAJERO!")

    def vol_tts_down(self):
        actual = self.stt.volume()
        nuevo = max(0.0, actual - 0.1)
        self.stt.setVolume(nuevo)
        self.anexar_linea("jugador", f"Volumen de narrador ajustado a {nuevo*100:.0f}%")
        if not self.is_reading:
            self.stt.say("¡HOLA VIAJERO!")
