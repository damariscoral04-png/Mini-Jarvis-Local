"""
Mini-JARVIS
Asistente de voz local: STT (Vosk) -> LLM (Ollama) -> TTS (pyttsx3)
"""

import sounddevice as sd
import pyttsx3
import ollama
import json
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)  # oculta los mensajes internos (LOG/WARNING) de la librería Vosk

# ============================================================
# CONFIGURACIÓN DEL LLM
# ============================================================
MODEL = "llama3.2:1b"
MAX_TURNOS_MEMORIA = 5

SYSTEM_PROMPT = (
    "Eres Mini-JARVIS, asistente de Damaris. Respondes cualquier pregunta del "
    "usuario de forma útil, corta, en español."
    "pero puedes hablar de cualquier tema."
)

# ============================================================
# CONFIGURACIÓN DEL STT LOCAL (VOSK)
# ============================================================
RUTA_MODELO_VOSK = "modelo_vosk"

# ============================================================
# MEMORIA DE CONVERSACIÓN
# ============================================================
historial = [{"role": "system", "content": SYSTEM_PROMPT}]


# ============================================================
# DISPOSITIVOS DE AUDIO
# ============================================================
def listar_dispositivos():
    """Muestra todos los dispositivos de entrada de audio detectados por el sistema."""
    print("\n--- Dispositivos de audio de ENTRADA disponibles ---")
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            print(f"  [{i}] {d['name']}  (canales de entrada: {d['max_input_channels']})")
    print("-----------------------------------------------------\n")


def obtener_device():
    """Selecciona el micrófono a usar (prioriza uno con 'WO Mic' en el nombre)."""
    dispositivos = sd.query_devices()

    for i, d in enumerate(dispositivos):
        if "wo mic" in d['name'].lower() and d['max_input_channels'] > 0:
            print(f"[Usando micrófono:] {d['name']}")
            return i, int(d['default_samplerate'])

    print(" No encontré automáticamente un dispositivo con 'WO Mic' en el nombre.")
    print(" (Revisa que WO Mic Client esté abierto y conectado, y que el driver")
    print(" virtual 'WO Mic Device' esté instalado en Windows, no solo la app.)")
    listar_dispositivos()

    try:
        idx = input("Escribe el número del dispositivo a usar (ENTER = micrófono por defecto): ").strip()
        if idx == "":
            info = sd.query_devices(kind='input')
            print(f"Usando micrófono por defecto: {info['name']}")
            return None, int(info['default_samplerate'])
        idx = int(idx)
        print(f"Usando micrófono: {dispositivos[idx]['name']}")
        return idx, int(dispositivos[idx]['default_samplerate'])
    except (ValueError, IndexError):
        print("Entrada inválida, uso el micrófono por defecto del sistema.")
        return None, 44100


# ============================================================
# STT - RECONOCIMIENTO DE VOZ (VOSK, OFFLINE)
# ============================================================
def cargar_modelo_vosk():
    """Carga el modelo de reconocimiento de voz offline (Vosk) desde RUTA_MODELO_VOSK."""
    print("[ Cargando modelo de voz local (Vosk)... ]")
    try:
        modelo = Model(RUTA_MODELO_VOSK)
    except Exception as e:
        print(f" Error al cargar el modelo de Vosk: {e}")
        print(f"   (¿Existe la carpeta '{RUTA_MODELO_VOSK}' junto a este script,")
        print("    con el modelo de https://alphacephei.com/vosk/models descomprimido?)")
        raise
    print("[ Modelo de voz cargado ]")
    return modelo


def escuchar(dev, freq, modelo_vosk):
    """Graba audio del micrófono durante 8 segundos y lo transcribe a texto con Vosk."""
    print("\n[ Escuchando ] (8 seg)...")
    try:
        audio = sd.rec(int(8 * freq), samplerate=freq, channels=1, dtype='int16', device=dev)
        sd.wait()
    except Exception as e:
        print(f" Error al grabar audio: {e}")
        return ""

    reconocedor = KaldiRecognizer(modelo_vosk, freq)

    try:
        reconocedor.AcceptWaveform(audio.tobytes())
        resultado = json.loads(reconocedor.Result())
        texto = resultado.get("text", "").strip()
    except Exception as e:
        print(f" Error al reconocer el audio: {e}")
        return ""

    if not texto:
        print(" No logré entender lo que dijiste, intenta de nuevo.")
        return ""

    print(f"TÚ: {texto}")
    return texto


# ============================================================
# TTS - SÍNTESIS DE VOZ
# ============================================================
def hablar(texto):
    """Convierte texto en voz y lo reproduce por los parlantes/audífonos."""
    print(f"JARVIS: {texto}")
    motor = pyttsx3.init()
    motor.setProperty('rate', 185)
    motor.say(texto)
    motor.runAndWait()
    motor.stop()


# ============================================================
# LLM - MOTOR DE RAZONAMIENTO (OLLAMA)
# ============================================================
def preguntar_llm(pregunta):
    """Envía la pregunta junto con el historial de conversación al LLM y devuelve la respuesta."""
    print("[ Pensando...]")

    mensajes = [historial[0]] + historial[1:][-(MAX_TURNOS_MEMORIA * 2):]
    mensajes.append({"role": "user", "content": pregunta})

    try:
        respuesta = ollama.chat(model=MODEL, messages=mensajes)
        texto = respuesta['message']['content'].strip()
    except Exception as e:
        print(f" Error al hablar con Ollama: {e}")
        print("   (¿Está corriendo la app de Ollama? ¿Descargaste el modelo con 'ollama pull llama3.2:1b'?)")
        return "Tuve un problema para pensar la respuesta, ¿puedes repetir la pregunta?"

    if not texto:
        texto = "No se me ocurrió una respuesta clara, ¿puedes reformular la pregunta?"

    historial.append({"role": "user", "content": pregunta})
    historial.append({"role": "assistant", "content": texto})
    return texto


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=== MINI-JARVIS LISTO ===")

    dev, freq = obtener_device()
    modelo_vosk = cargar_modelo_vosk()

    hablar("Hola Soy Mini-JARVIS, ¿en qué puedo ayudarte?")

    try:
        while True:
            entrada = input(
                "\nENTER + habla por el micrófono, o escribe tu pregunta y presiona ENTER: "
            ).strip()

            if entrada == "":
                pregunta = escuchar(dev, freq, modelo_vosk)
            else:
                pregunta = entrada
                print(f"TÚ: {pregunta}")

            if not pregunta:
                continue

            if "salir" in pregunta.lower():
                hablar("Hasta luego")
                break

            respuesta = preguntar_llm(pregunta)
            hablar(respuesta)

    except KeyboardInterrupt:
        print("\n\n Mini-JARVIS Apagado.")
        print("\n\n Mini-JARVIS estare aqui para lo que necesites.")