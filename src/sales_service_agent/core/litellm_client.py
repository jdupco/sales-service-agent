# src\sales_service_agent\core\litellm_client.py

from typing import Any

from litellm import completion, embedding
from litellm.types.utils import ModelResponse

from sales_service_agent.config import settings


def get_text_embeddings(texts: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos usando el modelo Nemotron vía NVIDIA API."""
    response: Any = embedding(
        model=f"openai/{settings.EMBEDDING_MODEL_NAME}",
        api_base=settings.NVIDIA_API_BASE,
        api_key=settings.NVIDIA_API_KEY,
        input=texts,
    )
    return [item["embedding"] for item in response.data]


def get_chat_response(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
) -> str:
    """Envía un historial de conversación al modelo DeepSeek vía OpenCode API."""
    response: ModelResponse = completion(
        model=f"openai/{settings.LLM_MODEL_NAME}",
        api_base=settings.OPENCODE_API_BASE,
        api_key=settings.OPENCODE_API_KEY,
        messages=messages,
        temperature=temperature,
    )
    content = response.choices[0].message.content
    return content if content is not None else ""
