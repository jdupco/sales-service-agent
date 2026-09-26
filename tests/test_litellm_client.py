from unittest.mock import MagicMock, patch

from sales_service_agent.core.litellm_client import (
    get_chat_response,
    get_text_embeddings,
)


@patch("sales_service_agent.core.litellm_client.embedding")
def test_get_text_embeddings_success(mock_embedding: MagicMock) -> None:
    """Valida que get_text_embeddings retorne la estructura de vectores esperada."""
    # Configuración del Mock
    fake_response = MagicMock()
    fake_response.data = [
        {"embedding": [0.1, 0.2, 0.3]},
        {"embedding": [0.4, 0.5, 0.6]},
    ]
    mock_embedding.return_value = fake_response

    # Ejecución
    input_texts = ["Texto 1", "Texto 2"]
    result = get_text_embeddings(input_texts)

    # Aseveraciones
    assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_embedding.assert_called_once()


@patch("sales_service_agent.core.litellm_client.completion")
def test_get_chat_response_success(mock_completion: MagicMock) -> None:
    """Valida que get_chat_response extraiga correctamente el texto generado por el LLM."""
    # Configuración del Mock
    fake_response = MagicMock()
    fake_message = MagicMock()
    fake_message.content = "Respuesta simulada del LLM"
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_response.choices = [fake_choice]
    mock_completion.return_value = fake_response

    # Ejecución
    messages = [{"role": "user", "content": "Hola"}]
    result = get_chat_response(messages)

    # Aseveraciones
    assert result == "Respuesta simulada del LLM"
    mock_completion.assert_called_once()


@patch("sales_service_agent.core.litellm_client.completion")
def test_get_chat_response_none_content(mock_completion: MagicMock) -> None:
    """Valida la resiliencia si el contenido retornado por el LLM es None."""
    # Configuración del Mock
    fake_response = MagicMock()
    fake_message = MagicMock()
    fake_message.content = None
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_response.choices = [fake_choice]
    mock_completion.return_value = fake_response

    # Ejecución
    messages = [{"role": "user", "content": "Hola"}]
    result = get_chat_response(messages)

    # Aseveraciones
    assert result == ""
    mock_completion.assert_called_once()
