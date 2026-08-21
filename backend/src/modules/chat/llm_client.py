"""
MODULE 6 - Step 4/5: CALL LLM & RECEIVE RESPONSE.

A thin provider-agnostic transport. Supports GPT-4 (OpenAI), Claude
(Anthropic) and Gemini (Google), plus a `mock` provider so the whole chat
pipeline is runnable and testable with no API key configured.

SDKs are imported lazily inside each provider so the module never forces a
dependency the deployment doesn't use.
"""
from abc import ABC, abstractmethod

from src.modules.chat.config import ChatSettings, get_chat_settings
from src.modules.chat.schemas import LLMResult


class LLMError(RuntimeError):
    """Raised when a provider call fails or is misconfigured."""


class BaseProvider(ABC):
    """Common interface every provider implements."""

    name: str = "base"

    def __init__(self, settings: ChatSettings):
        self.settings = settings
        self.model = settings.model

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        """Send the prompt pair and return a normalized result."""


class MockProvider(BaseProvider):
    """
    Deterministic offline provider.

    Used automatically when no API key is set, so the app runs end-to-end in
    development and CI. It echoes a short summary of the supplied context so
    developers can confirm the context builder is wired correctly.
    """

    name = "mock"

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        has_data = "Chưa có giao dịch nào" not in user_prompt
        body = (
            "[MOCK] Chưa cấu hình API key cho LLM nên đây là câu trả lời mẫu. "
            + (
                "Mình đã đọc được dữ liệu giao dịch của bạn và sẵn sàng phân tích "
                "khi bạn bật LLM thật."
                if has_data
                else "Hiện chưa có giao dịch nào trong hệ thống, bạn hãy tải sao kê lên trước nhé."
            )
        )
        return LLMResult(
            content=body,
            model=f"{self.model} (mock)",
            provider=self.name,
            usage=None,
        )


class AnthropicProvider(BaseProvider):
    """Claude 3 via the official `anthropic` SDK."""

    name = "anthropic"

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:  # pragma: no cover - depends on env
            raise LLMError(
                "Thiếu thư viện `anthropic`. Cài bằng: pip install anthropic"
            ) from exc

        client = AsyncAnthropic(
            api_key=self.settings.api_key,
            timeout=self.settings.CHAT_TIMEOUT_SECONDS,
        )
        response = await client.messages.create(
            model=self.model,
            max_tokens=self.settings.CHAT_MAX_TOKENS,
            temperature=self.settings.CHAT_TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = "".join(
            block.text for block in response.content
            if getattr(block, "type", None) == "text"
        )
        return LLMResult(
            content=text.strip(),
            model=response.model,
            provider=self.name,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )


class OpenAIProvider(BaseProvider):
    """GPT-4 family via the official `openai` SDK."""

    name = "openai"

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover - depends on env
            raise LLMError(
                "Thiếu thư viện `openai`. Cài bằng: pip install openai"
            ) from exc

        client = AsyncOpenAI(
            api_key=self.settings.api_key,
            timeout=self.settings.CHAT_TIMEOUT_SECONDS,
        )
        response = await client.chat.completions.create(
            model=self.model,
            max_tokens=self.settings.CHAT_MAX_TOKENS,
            temperature=self.settings.CHAT_TEMPERATURE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        usage = response.usage
        return LLMResult(
            content=(response.choices[0].message.content or "").strip(),
            model=response.model,
            provider=self.name,
            usage=(
                {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                }
                if usage
                else None
            ),
        )


class GeminiProvider(BaseProvider):
    """Gemini Pro via `google-generativeai`."""

    name = "gemini"

    async def complete(self, system_prompt: str, user_prompt: str) -> LLMResult:
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - depends on env
            raise LLMError(
                "Thiếu thư viện `google-generativeai`. "
                "Cài bằng: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self.settings.api_key)
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
        )
        response = await model.generate_content_async(
            user_prompt,
            generation_config={
                "max_output_tokens": self.settings.CHAT_MAX_TOKENS,
                "temperature": self.settings.CHAT_TEMPERATURE,
            },
        )
        return LLMResult(
            content=(response.text or "").strip(),
            model=self.model,
            provider=self.name,
        )


_PROVIDERS: dict[str, type[BaseProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "mock": MockProvider,
}


def get_provider(settings: ChatSettings | None = None) -> BaseProvider:
    """
    Resolve the configured provider.

    Falls back to `MockProvider` whenever no API key is present so that a
    fresh checkout works without any secrets.
    """
    settings = settings or get_chat_settings()

    if not settings.api_key and settings.provider != "mock":
        return MockProvider(settings)

    provider_cls = _PROVIDERS.get(settings.provider)
    if provider_cls is None:
        raise LLMError(
            f"Provider '{settings.provider}' không được hỗ trợ. "
            f"Chọn một trong: {', '.join(_PROVIDERS)}"
        )
    return provider_cls(settings)


async def call_llm(system_prompt: str, user_prompt: str) -> LLMResult:
    """Convenience one-shot call using the configured provider."""
    return await get_provider().complete(system_prompt, user_prompt)
