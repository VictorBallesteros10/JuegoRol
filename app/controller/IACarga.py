import subprocess
import requests
from app.service.Gestion_historia import GestionHistoria
from app.utilities.Textos import instrucciones


class IA:
    def __init__(self):
        self.hermes_process = None
        self.lmstudio_url = "http://localhost:1234/v1/chat/completions"
        self.Gestion_historia = GestionHistoria(self.lmstudio_url)

    def cargar_modelo(self):
        """Método para cargar el modelo en LMStudio."""
        try:
            directorio_lm_studio = r"C:\Users\jotxilla\AppData\Local\Programs\LM Studio" # Cambia esto a la ruta correcta de tu instalación de LMStudio
            # Desactivar el modelo actual
            self.hermes_process = subprocess.Popen(
                ['lms', 'unload', 'hermes-3-llama-3.2-3b'],
                cwd=directorio_lm_studio,
                shell=True
            )
            self.hermes_process.wait()
            # Cargar el nuevo modelo
            self.hermes_process = subprocess.Popen(
                ['lms', 'load', 'hermes-3-llama-3.2-3b'],
                cwd=directorio_lm_studio,
                shell=True
            )
            self.hermes_process.wait()
            print("Modelo cargado correctamente.")
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")

    def generar_texto(self, message, max_tokens=1000):
        #instrucciones.append({"role": "user", "content": message}) #creo que no es necesario por que le paso instrucciones por el otro lado
        try:
            response = requests.post(self.lmstudio_url, json={"messages": message, "max_tokens": max_tokens, "temperature": 0.2})
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error al generar el evento: {str(e)}"

