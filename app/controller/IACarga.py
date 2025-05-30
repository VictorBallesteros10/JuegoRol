import subprocess
import requests
from app.service.Gestion_historia import GestionHistoria
from app.utilities.Textos import instrucciones
import winreg

def encontrar_ruta_lm_studio():
    try:
        clave_registro = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        for raiz in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            with winreg.OpenKey(raiz, clave_registro) as clave_desinstalar:
                cantidad_subclaves = winreg.QueryInfoKey(clave_desinstalar)[0]
                for i in range(cantidad_subclaves):
                    try:
                        nombre_subclave = winreg.EnumKey(clave_desinstalar, i)
                        with winreg.OpenKey(clave_desinstalar, nombre_subclave) as subclave:
                            nombre_mostrado = winreg.QueryValueEx(subclave, "DisplayName")[0]
                            if "LM Studio" in nombre_mostrado:
                                ubicacion_instalacion = winreg.QueryValueEx(subclave, "InstallLocation")[0]
                                return ubicacion_instalacion
                    except FileNotFoundError:
                        continue
    except Exception as error:
        print("Error al buscar en el registro:", error)

    return None


class IA:
    def __init__(self):
        self.hermes_process = None
        self.lmstudio_url = "http://localhost:1234/v1/chat/completions"
        self.Gestion_historia = GestionHistoria(self.lmstudio_url)

    def cargar_modelo(self):
        try:
           # directorio_lm_studio = r"C:\Users\jotxilla\AppData\Local\Programs\LM Studio"
            directorio_lm_studio = encontrar_ruta_lm_studio()
            print(f"{directorio_lm_studio} ruta")
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

    def generar_texto(self, prompt) -> str:

        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = instrucciones + [{"role": "user", "content": prompt}]

        payload = {
            "model": "hermes-3-llama-3.2-3b",
            "messages": messages
        }
        resp = requests.post(self.lmstudio_url, json=payload)
        data = resp.json()

        choices = data.get("choices")
        if not choices or not isinstance(choices, list):
            raise RuntimeError(f"Respuesta inesperada de la IA: {data}")

        return choices[0]["message"]["content"].strip()

    def agregar_accion(self, accion: str, respuesta: str):

        self.Gestion_historia.registrar_accion(accion, respuesta)
