from sales_service_agent.core.litellm_client import (
    get_chat_response,
    get_text_embeddings,
)


def main() -> None:
    print("🔍 Probando conexión con NVIDIA API (Embeddings)...")
    try:
        sample_text = ["Prueba de concepto de embeddings Nemotron"]
        vectors = get_text_embeddings(sample_text)
        print(
            f"✅ NVIDIA Embeddings funcionando correctamente. Vector dimensión: {len(vectors[0])}"
        )
    except Exception as e:
        print(f"❌ Error en NVIDIA API: {e}")

    print("\n🔍 Probando conexión con OpenCode API (DeepSeek LLM)...")
    try:
        messages = [{"role": "user", "content": "Responde estrictamente la palabra 'CONECTADO'."}]
        response = get_chat_response(messages)
        print(f"✅ OpenCode LLM funcionando correctamente. Respuesta: {response}")
    except Exception as e:
        print(f"❌ Error en OpenCode API: {e}")


if __name__ == "__main__":
    main()
