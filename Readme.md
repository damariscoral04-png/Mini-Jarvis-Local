# Mini-JARVIS — Asistente de voz inteligente

## ¿Qué es Mini-JARVIS?
Mini-JARVIS es un asistente que puedes usar hablando o escribiendo. Tú le
preguntas algo, él lo piensa y te responde en voz alta. Además recuerda lo
que se habló antes en la misma conversación, para poder hacer preguntas
de seguimiento.

Todo el pipeline corre **de forma local**: el reconocimiento de voz (STT),
el modelo de lenguaje (LLM) y la síntesis de voz (TTS) funcionan sin
depender de servicios externos por internet.

## ¿Cómo se usa?
- **Hablando:** presiona ENTER sin escribir nada y habla por el micrófono.
- **Escribiendo:** escribe tu pregunta y presiona ENTER.
- **La respuesta** siempre se escucha en voz alta.
- **Para cerrarlo:** di o escribe "salir", o presiona Ctrl+C en la terminal.

## ¿Qué necesitas instalar antes de usarlo?

### 1. Ollama (el programa que hace pensar al asistente)
Descárgalo de https://ollama.com/download

Una vez instalado, abre una terminal y escribe:  ollama pull llama3.2:1b
Esto descarga el "cerebro" del asistente (solo se hace una vez).

### 2. Modelo de voz de Vosk (para que entienda lo que dices, sin internet)
1. Entra a https://alphacephei.com/vosk/models
2. Descarga el modelo en español **`vosk-model-small-es-0.42`** (~39 MB).
3. Descomprime el .zip. Vas a obtener una carpeta llamada
   `vosk-model-small-es-0.42`.
4. Mueve esa carpeta completa a la raíz del proyecto (junto a
   `Asistente.py`) y renómbrala a **`modelo_vosk`**.

La estructura final debe verse así:

Mini-Jarvis-vc/
└── modelo-vosk/
    ├── am/
    ├── conf/
    ├── graph/
    └── ivector/


> Esta carpeta **no está incluida en el repositorio** (pesa varios MB y no
> es contenido propio del equipo), por eso hay que descargarla aparte.
> Sin ella, el programa no va a poder cargar el reconocimiento de voz.

### 3. Librerías de Python

pip install -r Requerimientos.txt

## Micrófono
Usamos el celular como micrófono con la app **WO Mic**, porque el
micrófono de la laptop no funciona:
1. Abre **WO Mic Client** en la laptop y conéctalo al celular (por USB o
   WiFi). Debe decir "Connected". Solo funciona con Android y iPhone.
2. Al abrir `Asistente.py`, el programa busca el micrófono del celular
   solo. Si no lo encuentra, te muestra una lista de micrófonos para que
   elijas cuál usar.

## Cómo ejecutarlo
Con Ollama ya abierto en la laptop:   python Asistente.py

También hay un segundo programa aparte, `exploracion.py`, que sirve solo
para mostrarle cómo el modelo procesa una frase por dentro
(no es parte del asistente):     

python exploracion.py


## Archivos del proyecto
Mini-Jarvis-vc/
├── Asistente.py          → el asistente en sí (voz y texto)
├── exploracion.py        → muestra cómo piensa el modelo por dentro
├── Requerimientos.txt    → lista de librerías de Python que hay que instalar
├── modelo-vosk/          → modelo de voz de Vosk 
├── .gitignore
└── Readme.md

## Cosas que el asistente todavía no hace bien
- A veces puede inventar información que no es cierta es decir alucinaciones.
- No es bueno haciendo cuentas matemáticas exactas.
- Si la conversación es muy larga, puede olvidar cosas de al principio.
- El reconocimiento de voz (Vosk) es offline y liviano, así que a veces
  entiende mal frases muy cortas o con mucho ruido de fondo — es un poco
  menos preciso que servicios en la nube como Google, pero no necesita
  internet para funcionar.