import requests
from app.utilities.Textos import instrucciones


class GestionHistoria:
    def __init__(self, lmstudio_url: str):
        self.lmstudio_url = lmstudio_url
        self.historial = []
        self.resumen = ""
        self._summary_interval = 2

    def agregar_accion(self, jugador_input: str, ia_response: str):
        self.historial.append({
            'player': jugador_input,
            'gm': ia_response
        })
        # Cada N turnos, regeneramos el resumen
        if len(self.historial) % self._summary_interval == 0:
            self.actualizar_resumen()

    def registrar_accion(self, accion: str, respuesta: str):
        self.agregar_accion(accion, respuesta)

    def construir_prompt(self, jugador_input: str) -> list[dict]:
        messages = list(instrucciones)
        if self.resumen:
            messages.append({
                'role': 'system',
                'content': f"Resumen de la historia hasta ahora: {self.resumen}"
            })
        for turno in self.historial:
            messages.append({'role': 'user', 'content': turno['player']})
            messages.append({'role': 'assistant', 'content': turno['gm']})
        messages.append({'role': 'user', 'content': jugador_input})
        return messages

    def actualizar_resumen(self):
        if not self.historial:
            return
        resumen_prompt = [
            {'role': 'system', 'content': 'Eres un asistente que resume historias de rol.'},
            {'role': 'user', 'content': (
                'Resume brevemente la historia con los turnos de jugador y GM, condensando la información:\n' +
                '\n'.join(f"Jugador: {t['player']} -> GM: {t['gm']}" for t in self.historial)
            )}
        ]
        try:
            resp = requests.post(
                self.lmstudio_url,
                json={'messages': resumen_prompt, 'max_tokens': 500, 'temperature': 0.2}
            )
            data = resp.json()
            if data.get('choices'):
                self.resumen = data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error al actualizar resumen: {e}")

    def crear_resumen(self, historia: str) -> str:
        resumen_prompt = [
            {'role': 'system', 'content': 'Eres un asistente que resume historias de rol.'},
            {'role': 'user', 'content': (
                    'Resume brevemente la historia con los turnos de jugador y GM, condensando la información:\n' +
                    historia
            )}
        ]
        try:
            resp = requests.post(
                self.lmstudio_url,
                json={'messages': resumen_prompt, 'max_tokens': 500, 'temperature': 0.2}
            )
            data = resp.json()
            if data.get('choices'):
               self.resumen = data['choices'][0]['message']['content'].strip()
            return self.resumen
        except Exception as e:
            print(f"Error al actualizar resumen: {e}")

    def devolver_historia(self) -> str:
        self.actualizar_resumen()
        return self.resumen
