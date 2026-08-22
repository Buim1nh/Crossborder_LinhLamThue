"""
LLM Service - Pluggable interface for multiple LLM providers.
Currently supports DeepSeek (OpenAI-compatible API).
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional, Any

from src.core.config import get_settings


# ─── Config ─────────────────────────────────────────────────────────────────

DEEPSEEK_MODELS = {
    "deepseek-chat": "deepseek-chat",      # DeepSeek-V3 (cheap, fast)
    "deepseek-reasoner": "deepseek-reasoner",  # DeepSeek-R1 (slow, reasoning)
}
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


# ─── Response DTO ───────────────────────────────────────────────────────────

class LLMResponse:
    content: str
    model: str
    usage: Optional[dict] = None
    raw_response: Optional[dict] = None

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[dict] = None,
        raw_response: Optional[dict] = None,
    ):
        self.content = content
        self.model = model
        self.usage = usage
        self.raw_response = raw_response


# ─── Base ───────────────────────────────────────────────────────────────────

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, message: str, system_prompt: Optional[str] = None) -> LLMResponse:
        pass

    @abstractmethod
    async def analyze_transaction(self, transaction_data: dict) -> dict:
        pass

    @abstractmethod
    async def generate_report_summary(self, transactions: list[dict], period: str) -> str:
        pass


# ─── DeepSeek ──────────────────────────────────────────────────────────────

_DEEPSEEK_SYSTEM = """Bạn là trợ lý tài chính AI của Wealify.
Phân tích giao dịch ngân hàng tiếng Việt. Trả lời ngắn gọn, chính xác, hữu ích."""


_ANALYZE_SYSTEM = """Bạn là chuyên gia phân tích giao dịch tài chính.
Với dữ liệu giao dịch, hãy trả lời JSON với các trường:
- category: loại chi tiêu (Giải trí, Hóa đơn, Mua sắm, Ăn uống, Di chuyển, Thu nhập, Khác)
- merchant_identified: true/false - có nhận diện được merchant không
- merchant_name: tên merchant nếu nhận diện được
- is_subscription: true/false - có phải giao dịch định kỳ không
- subscription_name: tên dịch vụ định kỳ nếu là subscription
- alert_level: "regular" | "needs_confirmation" | "insufficient_data"
- alert_reason: lý do cảnh báo nếu có
- confidence: số 0.0-1.0 độ tin của phân tích
- notes: ghi chú ngắn bằng tiếng Việt"""


_SUMMARY_SYSTEM = """Bạn là chuyên gia tư vấn tài chính cá nhân.
Dựa trên danh sách giao dịch, viết báo cáo tóm tắt tiếng Việt gồm:
1. Tổng thu chi
2. Top 3 chi tiêu lớn nhất
3. Các khoản định kỳ phát hiện được
4. Đề xuất tiết kiệm (nếu có)
Giữ ngắn gọn, dễ hiểu."""


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.LLM_API_KEY
        self.model = self.settings.LLM_MODEL or DEFAULT_DEEPSEEK_MODEL

        if not self.api_key:
            raise RuntimeError(
                "LLM_API_KEY chưa được cấu hình. "
                "Vui lòng thêm DEEPSEEK_API_KEY vào biến môi trường."
            )

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise RuntimeError(
                "Package 'openai' chưa được cài. Chạy: pip install openai"
            ) from None

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=60.0,
            max_retries=2,
        )

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> LLMResponse:
        system = system_prompt or _DEEPSEEK_SYSTEM
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                temperature=0.3,
                stream=True,
            )
            content_chunks: list[str] = []
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    content_chunks.append(delta)

            full_content = "".join(content_chunks)
            return LLMResponse(content=full_content, model=self.model)
        except Exception as exc:
            raise RuntimeError(f"DeepSeek chat failed: {exc}") from exc

    async def analyze_transaction(self, transaction_data: dict) -> dict:
        msg = json.dumps(transaction_data, ensure_ascii=False, indent=2)
        prompt = f"""Phân tích giao dịch sau và trả lời CHỈ JSON (không chú thích gì khác):

{msg}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _ANALYZE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            result = json.loads(raw)

            # Ensure all required fields exist
            return {
                "category": result.get("category", "Khác"),
                "merchant_identified": bool(result.get("merchant_identified", False)),
                "merchant_name": result.get("merchant_name") or None,
                "is_subscription": bool(result.get("is_subscription", False)),
                "subscription_name": result.get("subscription_name") or None,
                "alert_level": result.get("alert_level", "regular"),
                "alert_reason": result.get("alert_reason") or None,
                "confidence": float(result.get("confidence", 0.0)),
                "notes": result.get("notes", ""),
            }
        except json.JSONDecodeError as exc:
            return {
                "category": "Khác",
                "merchant_identified": False,
                "is_subscription": False,
                "alert_level": "regular",
                "confidence": 0.0,
                "notes": f"Không phân tích được: {exc}",
            }
        except Exception as exc:
            return {
                "category": "Khác",
                "merchant_identified": False,
                "is_subscription": False,
                "alert_level": "regular",
                "confidence": 0.0,
                "notes": f"Lỗi LLM: {exc}",
            }

    async def generate_report_summary(
        self, transactions: list[dict], period: str
    ) -> str:
        # Summarize to avoid token overflow
        sample = transactions[:50]
        summary = []
        for t in sample:
            summary.append({
                "merchant": t.get("merchant_name") or t.get("description", "")[:40],
                "amount": t.get("amount"),
                "category": t.get("category", "Khác"),
                "is_subscription": t.get("is_subscription", False),
            })

        prompt = (
            f"Tạo báo cáo tóm tắt {period} cho {len(transactions)} giao dịch sau "
            f"(hiển thị mẫu {len(sample)} giao dịch đầu tiên):\n"
            f"{json.dumps(summary, ensure_ascii=False, indent=2)}\n"
            f"Tổng số giao dịch: {len(transactions)}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SUMMARY_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content or "Không tạo được báo cáo."
        except Exception as exc:
            return f"Không tạo được báo cáo: {exc}"


# ─── Placeholder ───────────────────────────────────────────────────────────

class PlaceholderLLM(BaseLLMProvider):
    def __init__(self):
        self.settings = get_settings()
        self.model = self.settings.LLM_MODEL

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> LLMResponse:
        return LLMResponse(
            content=f"[PLACEHOLDER] Received: {message[:100]}... (LLM not configured)",
            model=self.model or "none",
        )

    async def analyze_transaction(self, transaction_data: dict) -> dict:
        return {
            "category": "Khác",
            "merchant_identified": False,
            "is_subscription": False,
            "alert_level": "regular",
            "confidence": 0.0,
            "notes": "LLM chưa được cấu hình",
        }

    async def generate_report_summary(self, transactions: list[dict], period: str) -> str:
        total = sum(t.get("amount", 0) for t in transactions)
        return (
            f"Báo cáo {period}: {len(transactions)} giao dịch, "
            f"Tổng: {total:,.0f}đ. LLM chưa được cấu hình."
        )


# ─── Factory ───────────────────────────────────────────────────────────────

_PROVIDER_MAP = {
    "deepseek": DeepSeekProvider,
    "anthropic": None,   # TODO: implement AnthropicProvider
    "openai": None,      # TODO: implement OpenAIProvider
}


def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower().strip()

    if provider == "deepseek":
        return DeepSeekProvider()

    # TODO: add more providers here
    return PlaceholderLLM()


# ─── Convenience ─────────────────────────────────────────────────────────────

async def chat(message: str, system_prompt: Optional[str] = None) -> LLMResponse:
    provider = get_llm_provider()
    return await provider.chat(message, system_prompt)


async def analyze_transaction(transaction_data: dict) -> dict:
    provider = get_llm_provider()
    return await provider.analyze_transaction(transaction_data)


async def generate_summary(transactions: list[dict], period: str) -> str:
    provider = get_llm_provider()
    return await provider.generate_report_summary(transactions, period)
