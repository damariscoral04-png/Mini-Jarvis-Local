"""
DamJar
Asistente de voz local: STT (Vosk) -> LLM (Ollama) -> TTS (pyttsx3)
Nuevo: lectura de texto en imágenes (OCR con Tesseract) + resumen con el LLM
"""

import sounddevice as sd
import pyttsx3
import ollama
import json
import datetime      # funcion hora y fecha
import threading      # función temporizador
import os             # para revisar si el archivo de imagen existe
from vosk import Model, KaldiRecognizer, SetLogLevel
import pytesseract    # OCR: extrae texto de una imagen
from PIL import Image  # abre el archivo de imagen para pasárselo a pytesseract

SetLogLevel(-1)  # oculta los mensajes internos (LOG/WARNING) de la librería Vosk

# ============================================================
# CONFIGURACIÓN DEL LLM
# ============================================================
MODEL = "llama3.2:1b"
MAX_TURNOS_MEMORIA = 5

SYSTEM_PROMPT = (
    "Eres DamJar, asistente de Damaris. Respondes cualquier pregunta del "
    "usuario de forma útil, corta, en español, "
    "pero puedes hablar de cualquier tema."
)

# ============================================================
# CONFIGURACIÓN DEL STT LOCAL (VOSK)
# ============================================================
RUTA_MODELO_VOSK = "modelo_vosk"

# ============================================================
# CONFIGURACIÓN DEL OCR (TESSERACT)
# ============================================================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
    """Graba audio del micrófono durante 10 segundos y lo transcribe a texto con Vosk."""
    print("\n[ Escuchando ] (10 seg)...")
    try:
        audio = sd.rec(int(10 * freq), samplerate=freq, channels=1, dtype='int16', device=dev)
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

    print(f"🧑 TÚ: {texto}")
    return texto


# ============================================================
# TTS - SÍNTESIS DE VOZ
# ============================================================
def hablar(texto):
    """Convierte texto en voz y lo reproduce por los parlantes/audífonos."""
    print(f"🤖 DAMJAR: {texto}")
    motor = pyttsx3.init()
    motor.setProperty('rate', 185)
    motor.say(texto)
    motor.runAndWait()
    motor.stop()


# ============================================================
# NUEVAS
# ============================================================
PALABRAS_HORA = ["hora"]
PALABRAS_FECHA = ["día", "dia", "fecha"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def es_pregunta_de_hora(pregunta):
    """Detecta si el usuario preguntó por la hora y/o la fecha actual."""
    pregunta = pregunta.lower()
    return any(p in pregunta for p in PALABRAS_HORA) or any(p in pregunta for p in PALABRAS_FECHA)


def _hora_en_formato_12(ahora):
    """Convierte la hora a formato de 12 horas."""
    h = ahora.hour
    minuto = ahora.minute
    if h == 0:
        return f"12:{minuto:02d} de la madrugada"
    if h < 12:
        return f"{h}:{minuto:02d} de la mañana"
    if h == 12:
        return f"12:{minuto:02d} del mediodía"
    if h < 19:
        return f"{h - 12}:{minuto:02d} de la tarde"
    return f"{h - 12}:{minuto:02d} de la noche"


def responder_hora(pregunta):
    """Responde SOLO lo que se preguntó: hora, fecha, o ambas si se piden las dos."""
    pregunta = pregunta.lower()
    pidio_hora = any(p in pregunta for p in PALABRAS_HORA)
    pidio_fecha = any(p in pregunta for p in PALABRAS_FECHA)

    ahora = datetime.datetime.now()
    dia_semana = DIAS_SEMANA[ahora.weekday()]
    mes = MESES[ahora.month - 1]

    hora_str = f"son las {_hora_en_formato_12(ahora)}"

    if pidio_fecha and pidio_hora:
        return f"Hoy es {dia_semana} {ahora.day} de {mes}, y {hora_str}."
    if pidio_fecha:
        return f"Hoy es {dia_semana} {ahora.day} de {mes}."
    return f"{hora_str.capitalize()}."

# ============================================================
# Temporizador
# ============================================================
def es_pregunta_de_temporizador(pregunta):
    """Detecta si el usuario está pidiendo un temporizador."""
    return "temporizador" in pregunta.lower()

def extraer_tiempo(pregunta):
    """Busca el primer número en el texto y detecta si la unidad es segundos o minutos."""
    numero = None
    for palabra in pregunta.split():
        if palabra.isdigit():
            numero = int(palabra)
            break

    if numero is None:
        return None, None

    if "segundo" in pregunta.lower():
        return numero, "segundos"
    return numero, "minutos" 


def iniciar_temporizador(cantidad, unidad):
    """Arranca un temporizador en segundo plano (no bloquea el resto del programa)
    que avisa por voz cuando se cumple el tiempo, mostrando una cuenta regresiva
    visible en la consola."""
    segundos_totales = cantidad if unidad == "segundos" else cantidad * 60

    def contar_regresivo():
        restante = segundos_totales
        while restante > 0:
            mins, secs = divmod(restante, 60)
            print(f"\r[Temporizador] Tiempo restante: {mins:02d}:{secs:02d} ", end="", flush=True)
            threading.Event().wait(1)
            restante -= 1
        print("\r[Temporizador] Tiempo restante: 00:00 ")
        hablar(f"¡Se cumplió el temporizador de {cantidad} {unidad}!")

    threading.Thread(target=contar_regresivo, daemon=True).start()
    hablar(f"Temporizador iniciado por {cantidad} {unidad}.")


def es_pregunta_de_imagen(pregunta):
    """Detecta si el usuario quiere que se lea el texto de una imagen.
    Formato esperado: 'imagen <ruta del archivo>' """
    return pregunta.lower().startswith("imagen ")


def leer_texto_de_imagen(ruta_imagen):
    """Usa OCR (Tesseract) para extraer el texto que hay dentro de una imagen."""
    if not os.path.exists(ruta_imagen):
        return None
    try:
        img = Image.open(ruta_imagen)
        texto = pytesseract.image_to_string(img, lang="spa")
        return texto.strip()
    except Exception as e:
        print(f" Error al leer la imagen con OCR: {e}")
        return None


def resumir_texto_de_imagen(texto_extraido):
    """Le pide al LLM un resumen del texto que se extrajo de la imagen."""
    prompt_resumen = [
        {"role": "system", "content": "Resume el siguiente texto de forma breve y clara, en español."},
        {"role": "user", "content": texto_extraido},
    ]
    try:
        respuesta = ollama.chat(model=MODEL, messages=prompt_resumen)
        return respuesta['message']['content'].strip()
    except Exception as e:
        print(f" Error al resumir con Ollama: {e}")
        return "No pude generar el resumen, pero sí logré leer el texto de la imagen (mira la terminal)."


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
    print("=== DAMJAR LISTO ===")

    dev, freq = obtener_device()
    modelo_vosk = cargar_modelo_vosk()

    hablar("Hola, soy DamJar, ¿en qué puedo ayudarte?")

    try:
        while True:
            entrada = input(
                "\nENTER + habla por el micrófono, o escribe tu pregunta y presiona ENTER: "
            ).strip()

            if entrada == "":
                pregunta = escuchar(dev, freq, modelo_vosk)
            else:
                pregunta = entrada
                print(f"🧑 TÚ: {pregunta}")

            if not pregunta:
                continue

            if "salir" in pregunta.lower():
                hablar("Hasta luego")
                break

            # nuevas
            if es_pregunta_de_hora(pregunta):
                hablar(responder_hora(pregunta))
                continue

            if es_pregunta_de_temporizador(pregunta):
                cantidad, unidad = extraer_tiempo(pregunta)
                if cantidad:
                    iniciar_temporizador(cantidad, unidad)
                else:
                    hablar("¿De cuántos minutos o segundos quieres el temporizador?")
                continue

            if es_pregunta_de_imagen(pregunta):
                ruta_imagen = pregunta[len("imagen "):].strip()
                texto_extraido = leer_texto_de_imagen(ruta_imagen)

                if texto_extraido is None:
                    hablar("No encontré esa imagen, revisa que la ruta esté bien escrita.")
                elif not texto_extraido:
                    hablar("Abrí la imagen pero no logré leer texto en ella.")
                else:
                    print(f"\n[Texto extraído de la imagen]:\n{texto_extraido}\n")
                    resumen = resumir_texto_de_imagen(texto_extraido)
                    hablar(f"Esto es lo que dice la imagen, resumido: {resumen}")
                continue

        
            respuesta = preguntar_llm(pregunta)
            hablar(respuesta)

    except KeyboardInterrupt:
        print("\n\n DamJar Apagado.")
        print("\n\n DamJar estare aqui para lo que necesites.")