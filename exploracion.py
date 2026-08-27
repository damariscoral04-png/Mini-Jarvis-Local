"""
EXPLORACION DE ARQUITECTURA - Transformer
Tokenización | Embeddings | Atención | Limitaciones
"""

from transformers import AutoTokenizer, AutoModel
import torch

NOMBRE_MODELO = "bert-base-uncased"

tokenizador = AutoTokenizer.from_pretrained(NOMBRE_MODELO)
modelo = AutoModel.from_pretrained(NOMBRE_MODELO, output_attentions=True)


def analizar_arquitectura(texto_prueba):
    """Muestra, para una frase de ejemplo, la tokenización y los pesos de atención del modelo."""
    print("=" * 70)
    print("EXPLORACIÓN DEL MODELO - ARQUITECTURA TRANSFORMER")
    print("=" * 70)
    print(f"\nFrase de entrada: {texto_prueba}")
    print("-" * 70)

    # --- 1. TOKENIZACIÓN ---
    tokens = tokenizador.tokenize(texto_prueba)
    entradas = tokenizador(texto_prueba, return_tensors="pt")

    print("\n1) TOKENIZACIÓN")
    print(f"   Tokens: {tokens}")
    print(f"   Cantidad de tokens: {len(tokens)}")
    print(f"   IDs numéricos: {entradas['input_ids'].tolist()[0]}")

    # --- 2, 3 y 4. EMBEDDING + ATENCIÓN + ACTUALIZACIÓN POR CONTEXTO ---
    with torch.no_grad():
        salidas = modelo(**entradas)
        atencion_ultima_capa = salidas.attentions[-1]

    print("\n2) EMBEDDING")
    print(f"   Dimensión del vector por token: {salidas.last_hidden_state.shape[2]}")

    print("\n3) ATENCIÓN (self-attention)")
    print(f"   Cabeceras de atención en la última capa: {atencion_ultima_capa.shape[1]}")
    print("   Cada token calcula un peso de atención hacia todos los demás tokens.")

    # --- 5. PREDICCIÓN CON SOFTMAX ---
    print("\n4) PREDICCIÓN (softmax)")
    print("   Softmax convierte los valores del modelo en probabilidades")
    print("   y se elige el token más probable como siguiente palabra.")

    # --- 6. REPETICIÓN ---
    print("\n5) REPETICIÓN")
    print("   El token elegido se agrega al texto y el proceso se repite")
    print("   hasta llegar a un límite o a un token de fin de secuencia.")

    # --- LIMITACIONES ---
    print("\n" + "=" * 70)
    print("LIMITACIONES DEL MODELO")
    print("=" * 70)
    print("- Alucinaciones: puede inventar información con total confianza.")
    print("- Razonamiento matemático: falla con cálculos numéricos exactos.")
    print("- Contexto largo: la atención se diluye y pierde información antigua.")
    print("- Sesgos: hereda los sesgos del corpus de entrenamiento.")
    print("- Sin memoria real: no recuerda nada fuera del contexto actual.")


if __name__ == "__main__":
    analizar_arquitectura(
        "DamJar usa inteligencia artificial basada en la arquitectura Transformer."
    )