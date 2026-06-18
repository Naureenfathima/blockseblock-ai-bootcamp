"""
Provider implementation for AWS Bedrock.

AWS Bedrock = access to multiple model families (Claude via Anthropic, Llama via
Meta, Mistral, Titan via Amazon) through a unified AWS API. Everything stays
inside your AWS VPC. Common in enterprise environments already on AWS — it
consolidates AI spend inside existing AWS contracts and satisfies data residency
and compliance requirements.

To use this provider, set in .env:
  LLM_PROVIDER=bedrock
  AWS_ACCESS_KEY_ID=your_key
  AWS_SECRET_ACCESS_KEY=your_secret
  AWS_REGION=us-east-1
  BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

Example BEDROCK_MODEL_IDs:
  - anthropic.claude-3-sonnet-20240229-v1:0  (Claude via Bedrock)
  - anthropic.claude-3-haiku-20240307-v1:0
  - meta.llama3-8b-instruct-v1:0             (Llama via Bedrock)
  - meta.llama3-70b-instruct-v1:0
  - mistral.mistral-7b-instruct-v0:2         (Mistral via Bedrock)

Requires boto3 package: pip install boto3
"""
import json
from typing import Optional, List

from shared.config import settings
from shared.providers.base import LLMProvider, LLMResponse


class BedrockProvider(LLMProvider):
    """
    AWS Bedrock via boto3, using Bedrock's unified `converse` API.

    The `converse` API accepts a messages array similar to OpenAI's format,
    which keeps the translation layer minimal. Tool calling is supported via
    Bedrock's toolConfig format.
    """

    def __init__(self) -> None:
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for LLM_PROVIDER=bedrock. "
                "Install it: pip install boto3"
            )

        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self._model_id = settings.bedrock_model_id
        self._provider_name = "bedrock"

    async def chat(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[dict]] = None,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """
        Send a chat request via Bedrock's converse API.

        The converse API handles Claude, Llama, and Mistral models through a
        single unified interface — we just change BEDROCK_MODEL_ID in .env.
        """
        # Extract system message (Bedrock passes it separately, like Anthropic).
        system_content = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_content += msg["content"] + "\n"
            else:
                user_messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

        # JSON mode: Bedrock doesn't have a native JSON mode — inject instruction.
        # This is a prompting workaround; parsing should remain tolerant.
        if response_format and response_format.get("type") == "json_object":
            system_content += "\nRespond with valid JSON only, no other text or markdown."

        request: dict = {
            "modelId": self._model_id,
            "messages": user_messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system_content.strip():
            request["system"] = [{"text": system_content.strip()}]

        # Translate OpenAI-style tool schemas to Bedrock's toolConfig format.
        if tools:
            tool_specs = []
            for tool in tools:
                fn = tool.get("function", {})
                tool_specs.append({
                    "toolSpec": {
                        "name": fn.get("name", ""),
                        "description": fn.get("description", ""),
                        "inputSchema": {"json": fn.get("parameters", {})},
                    }
                })
            request["toolConfig"] = {"tools": tool_specs}

        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self._client.converse(**request))

        # Normalize the response into LLMResponse.
        output = response.get("output", {}).get("message", {})
        content_blocks = output.get("content", [])

        text_parts = []
        normalized_tool_calls = []

        for block in content_blocks:
            if "text" in block:
                text_parts.append(block["text"])
            elif "toolUse" in block:
                tool_use = block["toolUse"]
                normalized_tool_calls.append({
                    "id": tool_use.get("toolUseId", ""),
                    "name": tool_use.get("name", ""),
                    "arguments": tool_use.get("input", {}),
                })

        return LLMResponse(
            content="\n".join(text_parts) if text_parts else None,
            tool_calls=normalized_tool_calls,
            raw=response,
            provider="bedrock",
            model=self._model_id,
        )

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError(
            "AWS Bedrock does not provide speech transcription through this provider. "
            "For STT, use Amazon Transcribe (a separate AWS service) or set "
            "VOICE_PROVIDER=groq or VOICE_PROVIDER=openai. "
            "See docs/provider-setup-guide.md for options."
        )

    async def synthesize_speech(self, text: str, voice: str = "default") -> bytes:
        raise NotImplementedError(
            "AWS Bedrock does not provide TTS through this provider. "
            "For TTS, use Amazon Polly (a separate AWS service) or set "
            "VOICE_PROVIDER=openai. "
            "See docs/provider-setup-guide.md for options."
        )
