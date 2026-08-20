"""
LLM Service - Pluggable interface for multiple LLM providers.

Currently a placeholder - to be configured with Claude/GPT-4o/Gemini.
"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from src.core.config import get_settings


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model: str
    usage: Optional[dict] = None
    raw_response: Optional[dict] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(self, message: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Send a chat message and get response."""
        pass
    
    @abstractmethod
    async def analyze_transaction(self, transaction_data: dict) -> dict:
        """Analyze a single transaction."""
        pass
    
    @abstractmethod
    async def generate_report_summary(self, transactions: list[dict], period: str) -> str:
        """Generate a natural language summary of transactions."""
        pass


class PlaceholderLLM(BaseLLMProvider):
    """
    Placeholder LLM for development/testing.
    
    Replace this with actual provider (Claude/GPT-4o/Gemini) when ready.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.model = self.settings.LLM_MODEL
    
    async def chat(self, message: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Placeholder chat - returns a mock response.
        
        TODO: Replace with actual LLM call
        """
        # Placeholder response
        return LLMResponse(
            content=f"[PLACEHOLDER] Received message: {message[:100]}... (LLM not configured)",
            model=self.model,
        )
    
    async def analyze_transaction(self, transaction_data: dict) -> dict:
        """
        Placeholder transaction analysis.
        
        TODO: Implement with actual LLM for:
        - Categorization
        - Anomaly detection
        - Merchant identification
        - Spending pattern analysis
        """
        return {
            "category": "uncategorized",
            "merchant_identified": False,
            "is_subscription": False,
            "alert_level": "regular",
            "confidence": 0.0,
            "notes": "LLM not configured - placeholder response"
        }
    
    async def generate_report_summary(self, transactions: list[dict], period: str) -> str:
        """
        Placeholder report generation.
        
        TODO: Implement with actual LLM for natural language summaries.
        """
        total = sum(t.get("amount", 0) for t in transactions)
        return f"[PLACEHOLDER] This is a {period} spending summary. Total transactions: {len(transactions)}, Total amount: ${total:.2f}. LLM not configured."


# Factory function to get the configured LLM provider
def get_llm_provider() -> BaseLLMProvider:
    """
    Get the configured LLM provider based on settings.
    
    TODO: Implement provider selection when LLM is chosen:
    - if provider == "anthropic": return AnthropicProvider()
    - elif provider == "openai": return OpenAIProvider()
    - elif provider == "gemini": return GeminiProvider()
    """
    return PlaceholderLLM()


# Convenience function for quick access
async def chat(message: str, system_prompt: Optional[str] = None) -> LLMResponse:
    """Quick access to LLM chat."""
    provider = get_llm_provider()
    return await provider.chat(message, system_prompt)


async def analyze_transaction(transaction_data: dict) -> dict:
    """Quick access to transaction analysis."""
    provider = get_llm_provider()
    return await provider.analyze_transaction(transaction_data)


async def generate_summary(transactions: list[dict], period: str) -> str:
    """Quick access to report summary generation."""
    provider = get_llm_provider()
    return await provider.generate_report_summary(transactions, period)
