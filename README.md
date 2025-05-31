
# 🎮 Juego de Rol Narrativo con IA

Este es un juego de rol narrativo inspirado en Dungeons & Dragons, donde una Inteligencia Artificial actúa como Game Master. Los jugadores pueden crear su personaje, interactuar con la historia y tomar decisiones que influyen en el desarrollo de la aventura.

## ✅ Requisitos

Antes de ejecutar el proyecto, asegúrate de tener lo siguiente:

### 1. ✅ Python
- **Versión recomendada**: Python 3.10 o superior
- Puedes descargarlo desde: https://www.python.org/downloads/

### 2. ✅ Entorno de desarrollo (opcional)
Puedes usar cualquier IDE, pero se recomienda uno de los siguientes para facilitar la ejecución:
- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Thonny](https://thonny.org/) (ideal para principiantes)

### 3. ✅ Instalar dependencias

Abre una terminal en la raíz del proyecto y ejecuta:

\`\`\`bash
# Crear y activar entorno virtual
python -m venv .venv
# En Linux/Mac:
source .venv/bin/activate
# En Windows (PowerShell):
.venv\Scripts\Activate

# Una vez activado el entorno virtual, instala las dependencias
pip install -r requirements.txt
\`\`\`

### 4. ✅ LM Studio (para ejecutar la IA localmente)

Este proyecto usa un modelo de lenguaje local a través de **LM Studio**. Debes instalarlo y cargar un modelo compatible (por ejemplo, DeepSeek o similar).

- Descarga LM Studio desde: https://lmstudio.ai/

---

## 🚀 Cómo ejecutar el juego

1. Una vez instalados todos los requisitos, abre una terminal en la raíz del proyecto.

2. Ejecuta el archivo principal del juego:

\`\`\`bash
python run.py
\`\`\`

3. En la pantalla de inicio, haz clic en **"Registrar"** para crear una nueva cuenta y comenzar tu aventura.

---

## 📁 Estructura del Proyecto

\`\`\`
JuegoRol/
├── run.py                # Archivo principal para ejecutar el juego
├── requirements.txt      # Dependencias necesarias
├── archivos/             # Carpeta con imágenes, música y recursos
├── view/                 # Interfaz gráfica del juego (PyQt5)
├── services/             # Lógica del juego e interacción con IA
├── models/               # Clases del jugador, estados, etc.
├── utils/                # Funciones auxiliares y control de comandos
\`\`\`

---

## ℹ️ Notas adicionales

- La música e imágenes se cargan desde la carpeta \`archivos/\`. Puedes personalizarlas si lo deseas.
- Asegúrate de que LM Studio esté ejecutando el modelo **antes** de iniciar el juego para evitar errores de conexión con la IA.

---

¡Disfruta del juego y deja que tu imaginación sea tu mayor arma! 🐉🧙‍♂️⚔️
