# DamJar — Asistente de voz inteligente

## ¿Qué es DamJar?
DamJar es un asistente que puedes usar hablando o escribiendo. Tú le
preguntas algo, él lo piensa y te responde en voz alta. Además recuerda lo
que se habló antes en la misma conversación, para poder hacer preguntas
de seguimiento.

Todo el pipeline corre **de forma local**: el reconocimiento de voz (STT),
el modelo de lenguaje (LLM) y la síntesis de voz (TTS) funcionan sin
depender de servicios externos por internet.

> **Nota:** DamJar es un asistente basado en inteligencia artificial (un
> modelo de lenguaje). Sus respuestas pueden contener errores o
> información inventada (alucinaciones), así que conviene verificar
> cualquier dato importante antes de darlo por cierto.

## ¿Cómo se usa?
- **Hablando:** presiona ENTER sin escribir nada y habla por el micrófono.
- **Escribiendo:** escribe tu pregunta y presiona ENTER.
- **La respuesta** siempre se escucha en voz alta.
- **Para cerrarlo:** di o escribe "salir", o presiona Ctrl+C en la terminal.

## Funciones nuevas
Además de conversar, el asistente puede:
- Decirte la **hora y fecha actual** ("¿qué hora es?").
- Poner un **temporizador** ("temporizador de 5 minutos"), que avisa por
  voz cuando se cumple, sin dejar de poder seguir usando el asistente
  mientras tanto. (Funciona mejor escribiéndolo que diciéndolo por voz.)
- **Leer el texto de una imagen y resumirlo.** Escribe:
  ```
  imagen C:\ruta\a\tu\imagen.png
  ```
  El asistente extrae el texto de la imagen (usando OCR) y te da un
  resumen hablado de lo que dice. Funciona con capturas de pantalla o
  fotos de texto (documentos, apuntes, etc.), no con fotos de paisajes
  u objetos sin texto.

## ¿Qué necesitas instalar antes de usarlo?

### 1. Ollama (el programa que hace pensar al asistente)
Descárgalo de https://ollama.com/download

Una vez instalado, abre una terminal y escribe:
```
ollama pull llama3.2:1b
```
Esto descarga el "cerebro" del asistente (solo se hace una vez).

> Usamos `llama3.2:1b` (la versión más liviana de Llama 3.2, de 1 billón
> de parámetros) en lugar de una versión más grande, porque al probar
> modelos más pesados el proceso se interrumpía por falta de memoria
> RAM/VRAM disponible en el equipo de desarrollo. Es un ejemplo real del
> compromiso entre tamaño del modelo y recursos de hardware disponibles.

### 2. Modelo de voz de Vosk (para que entienda lo que dices, sin internet)
1. Entra a https://alphacephei.com/vosk/models
2. Descarga el modelo en español **`vosk-model-small-es-0.42`** (~39 MB).
3. Descomprime el .zip. Vas a obtener una carpeta llamada
   `vosk-model-small-es-0.42`.
4. Mueve esa carpeta completa a la raíz del proyecto (junto a
   `Asistente.py`) y renómbrala a **`modelo_vosk`**.

La estructura final debe verse así:
```
Mini-Jarvis-vc/
└── modelo_vosk/
    ├── am/
    ├── conf/
    ├── graph/
    └── ivector/
```

> Esta carpeta **no está incluida en el repositorio** (pesa varios MB y no
> es contenido propio del equipo), por eso hay que descargarla aparte.
> Sin ella, el programa no va a poder cargar el reconocimiento de voz.
> Por eso también debe estar listada en el `.gitignore`, junto con
> `__pycache__/` y los archivos `.pyc`, para no subirla por accidente al
> repositorio.

### 3. Tesseract OCR (para poder leer texto de imágenes)
1. Descarga el instalador desde:
   https://github.com/UB-Mannheim/tesseract/wiki
2. Durante la instalación, en la pantalla de idiomas adicionales, marca
   **Spanish** (si no lo haces, el OCR va a intentar leer todo en inglés).
3. Si lo instalas en una carpeta distinta a
   `C:\Program Files\Tesseract-OCR\`, ajusta esa ruta dentro de
   `Asistente.py` (línea `pytesseract.pytesseract.tesseract_cmd = ...`).

### 4. Librerías de Python
```
pip install -r Requerimientos.txt
```

> `Requerimientos.txt` debe incluir tanto las librerías que usa
> `Asistente.py` (`sounddevice`, `pyttsx3`, `ollama`, `vosk`,
> `pytesseract`, `pillow`) como las que usa `exploracion.py`
> (`transformers`, `torch`), para que el proyecto completo pueda
> instalarse y ejecutarse de una sola vez en otra máquina.

## Micrófono
Usamos el celular como micrófono con la app **WO Mic**, porque el
micrófono de la laptop no funciona:
1. Abre **WO Mic Client** en la laptop y conéctalo al celular (por USB o
   WiFi). Debe decir "Connected". Solo funciona con Android y iPhone.
2. Al abrir `Asistente.py`, el programa busca el micrófono del celular
   solo. Si no lo encuentra, te muestra una lista de micrófonos para que
   elijas cuál usar.

## Cómo ejecutarlo
Con Ollama ya abierto en la laptop:
```
python Asistente.py
```

También hay un segundo programa aparte, `exploracion.py`, que sirve solo
para mostrar cómo el modelo procesa una frase por dentro (tokenización,
embeddings y atención) — no es parte del asistente:
```
python exploracion.py
```

## Archivos del proyecto
```
Mini-Jarvis-vc/
├── Asistente.py          → el asistente en sí (voz, texto e imágenes)
├── exploracion.py        → muestra cómo piensa el modelo por dentro
├── Requerimientos.txt    → lista de librerías de Python que hay que instalar
├── modelo_vosk/          → modelo de voz de Vosk (se descarga aparte, ver arriba)
├── .gitignore
└── Readme.md
```

## Cosas que el asistente todavía no hace bien
- A veces puede inventar información que no es cierta, es decir,
  alucinaciones.
- No es bueno haciendo cuentas matemáticas exactas.
- Si la conversación es muy larga, puede olvidar cosas de al principio.
- El reconocimiento de voz (Vosk) es offline y liviano, así que a veces
  entiende mal frases muy cortas o con mucho ruido de fondo — es un poco
  menos preciso que servicios en la nube como Google, pero no necesita
  internet para funcionar.
- Las respuestas pueden tardar unos segundos o minutos en aparecer, dependiendo de
  qué tan rápida sea la laptop donde corre (el modelo piensa localmente,
  sin usar servidores externos).
- La lectura de imágenes (OCR) solo funciona bien con texto claro y
  legible; no describe fotos sin texto.