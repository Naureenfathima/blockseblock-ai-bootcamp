"""
Provider implementation that wraps the Cohere Chat API.

Key differences from the OpenAI API that this class handles transparently:
  1. Cohere splits conversations into a `message` (current turn) + `chat_history`
     (prior turns), rather than a single flat `messages` array.
  2. Cohere's tool schema format uses "parameter_definitions" instead of "parameters".
  3. JSON mode is not a native API feature — we approximate it via prompting.
  4. Cohere does not provide speech (STT/TTS) APIs.
"""
import cohere
from typing import Optional, List

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse


def _split_messages(messages: List[dict]) -> tuple[str, str, List[dict]]:
    """
    Split an OpenAI-style messages list into (system_preamble, current_message, history).

    Cohere's API expects:
      - `preamble`: a system instruction string (optional)
      - `message`: the latest user message (required)
      - `chat_history`: all prior turns in Cohere's own format

    This function extracts these three pieces from a flat OpenAI-style messages list.
    """
    preamble_parts: List[str] = []
    history: List[dict] = []
    current_user_message = ""

    # Walk the messages; the last user message becomes `message`, everything else
    # becomes history (or preamble for system messages).
    user_messages = [m for m in messages if m["role"] == "user"]
    current_user_message = user_messages[-1]["content"] if user_messages else ""

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            preamble_parts.append(content)
        elif msg is user_messages[-1]:
            # This is the current turn — skip it in history.
            continue
        elif role == "user":
            history.append({"role": "USER", "message": content})
        elif role == "assistant":
            history.append({"role": "CHATBOT", "message": content})

    return "\n\n".join(preamble_parts), current_user_message, history


def _translate_tools(openai_tools: List[dict]) -> List[dict]:
    """
    Convert OpenAI-style tool schemas to Cohere's format.

    OpenAI:  {"type": "function", "function": {"name", "description", "parameters": <JSON Schema>}}
    Cohere:  {"name", "description", "parameter_definitions": {"param": {"description", "type", "required"}}}
    """
    cohere_tools = []
    for tool in openai_tools:
        fn = tool.get("function", {})
        props = fn.get("parameters", {}).get("properties", {})
        required = fn.get("parameters", {}).get("required", [])

        param_defs = {}
        for param_name, schema in props.items():
            param_defs[param_name] = {
                "description": schema.get("description", ""),
                "type": schema.get("type", "str"),
                "required": param_name in required,
            }

        cohere_tools.append(
            {
                "name": fn["name"],
                "description": fn.get("description", ""),
                "parameter_definitions": param_defs,
            }
        )
    return cohere_tools


class CohereProvider(LLMProvider):
    """Talks to the Cohere Chat API with full translation to/from the common interface."""

    def __init__(self) -> None:
        self._api_key = settings.cohere_api_key
        self._model = settings.cohere_model
        self._client = cohere.AsyncClientV2(api_key=self._api_key)

    async def chat(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[dict]] = None,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """Send messages to the Cohere API and return a normalized response."""
        preamble, current_message, history = _split_messages(messages)

        # Cohere doesn't have native JSON mode — same prompting workaround as Anthropic.
        # Parsing code should remain tolerant (try/except around json.loads).
        if response_format and response_format.get("type") == "json_object":
            preamble += "\n\nRespond with valid JSON only. Do not include any explanation, markdown, or text outside the JSON object."

        kwargs: dict = {}
        if preamble:
            kwargs["preamble"] = preamble
        if history:
            kwargs["chat_history"] = history
        if tools:
            kwargs["tools"] = _translate_tools(tools)

        response = await self._client.chat(
            model=self._model,
            message=current_message,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Normalize tool calls from Cohere's format to our common format.
        normalized_tool_calls: list[dict] = []
        if response.tool_calls:
            for tc in response.tool_calls:
                normalized_tool_calls.append(
                    {
                        "id": getattr(tc, "id", tc.name),
                        "name": tc.name,
                        # Cohere returns parameters as a dict already.
                        "arguments": tc.parameters or {},
                    }
                )

        return LLMResponse(
            content=response.text,
            tool_calls=normalized_tool_calls,
            raw={"text": response.text, "generation_id": response.generation_id},
            provider="cohere",
            model=self._model,
        )

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError(
            "Cohere does not provide speech APIs. "
            "Set VOICE_PROVIDER=openai (or another speech-capable provider) in .env "
            "to use voice features while keeping LLM_PROVIDER=cohere for chat. "
            "See docs/provider-setup-guide.md for details."
        )

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "Cohere does not provide speech APIs. "
            "Set VOICE_PROVIDER=openai (or another speech-capable provider) in .env "
            "to use voice features while keeping LLM_PROVIDER=cohere for chat. "
            "See docs/provider-setup-guide.md for details."
        )
