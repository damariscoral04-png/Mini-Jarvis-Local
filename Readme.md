# Mini-JARVIS — Asistente de voz inteligente
Proyecto Integrador | Redes Neuronales | CENESTUR

## Descripción
Asistente conversacional local que implementa el pipeline STT → LLM → TTS
sobre la arquitectura Transformer, con memoria de conversación y manejo de
errores. Se puede interactuar por voz o por texto en cualquier turno.

## Modos de uso
- 🎤 **Por voz:** presiona ENTER y habla por el micrófono
- ⌨️ **Por texto:** escribe tu pregunta directamente
- 🔊 **Salida:** la respuesta siempre se reproduce por voz

## Estructura del proyecto
```
Mini-Jarvis-vc/
├── Asistente.py         → asistente completo (voz y texto)
├── exploracion.py        → módulo de exploración del modelo (tokenización, embeddings, atención)
├── Requerimientos.txt     → dependencias
├── .gitignore
├── Readme.md
└── ffmpeg.exe
```

## Instalación
```bash
pip install -r Requerimientos.txt
```
Necesitas además tener **Ollama** instalado y corriendo, con el modelo descargado:
```bash
ollama pull llama3.2
```
Y **ffmpeg** instalado en el sistema (o su ejecutable disponible en el PATH) para que
Whisper pueda procesar el audio.

## Ejecución
```bash
# Asistente de voz y texto
python Asistente.py

# Exploración de la arquitectura Transformer
python exploracion.py
```

## Proceso interno del modelo (identificación)
1. **Tokenización**: el texto se divide en tokens (~30-50 según el idioma).
2. **Embedding**: cada token se convierte en un vector de alta dimensión.
3. **Atención + feed-forward**: cada token "mira" a todos los demás para
   construir una representación contextual.
4. **Actualización por contexto**: cada capa refina el significado del token.
5. **Predicción con softmax**: se calcula la probabilidad del siguiente token.
6. **Repetición**: el proceso se repite hasta terminar la respuesta.

Ver `exploracion.py` para la demostración con una frase de ejemplo real.

## Limitaciones conocidas
- Alucinaciones (puede inventar información).
- Dificultad con razonamiento matemático exacto.
- Pérdida de contexto en conversaciones muy largas.
- Sesgos heredados del corpus de entrenamiento.
- No tiene memoria real fuera del contexto de la conversación actual.