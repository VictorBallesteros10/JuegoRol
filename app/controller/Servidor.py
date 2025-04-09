from flask import Flask, request, jsonify
from app.controller.IACarga import IA

app = Flask(__name__)
ia_instance = IA()

@app.route('/conversacion', methods=['POST'])
def start_conversation():
    """Recibe un mensaje del usuario y lo envía a la IA."""
    if ia_instance.hermes_process is None:
        ia_instance.cargar_modelo()

    data = request.json
    mensaje_usuario = data.get("mensaje", "")

    if not mensaje_usuario:
        return jsonify({"error": "No se recibió un mensaje válido."}), 400

    respuesta_ia = ia_instance.generar_texto(mensaje_usuario)

    return jsonify({"response": respuesta_ia})
