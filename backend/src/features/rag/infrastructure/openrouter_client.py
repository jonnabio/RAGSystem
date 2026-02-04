"""OpenRouter LLM client implementation."""

import httpx
from typing import List, Dict, Any, Optional
import logging
from src.features.rag.domain.interfaces import Message, LLMResponse

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    OpenRouter API client for multi-model LLM access.

    Supports thousands of models including free and paid options.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        app_name: str = "RAG System",
        timeout: float = 60.0
    ):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            base_url: API base URL
            app_name: Application name for tracking
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.app_name = app_name
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/yourusername/rag-system",
                "X-Title": app_name
            },
            timeout=timeout
        )

    async def generate(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: Conversation messages
            model: Model identifier (e.g., "meta-llama/llama-3-70b-instruct")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters

        Returns:
            LLM response

        Raises:
            RuntimeError: If API call fails
        """
        if not messages:
            raise ValueError("Messages cannot be empty")

        # Convert Message objects to dicts
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        payload = {
            "model": model,
            "messages": message_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            # Extract response
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")

            # Extract usage info
            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)

            # Calculate cost (if available)
            cost = self._calculate_cost(data, tokens_used)

            logger.info(
                f"Generated response from {model}: "
                f"{tokens_used} tokens, cost: ${cost:.4f}"
            )

            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                finish_reason=finish_reason
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenRouter: {e}")
            raise RuntimeError(f"OpenRouter API error: {e.response.text}")
        except httpx.TimeoutException:
            logger.error("Request to OpenRouter timed out")
            raise RuntimeError("Request timed out")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.

        Returns:
            List of model information dicts
        """
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            logger.info(f"Retrieved {len(models)} available models")
            return models

        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []

    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.

        Args:
            model_id: Model identifier

        Returns:
            Model information dict or None if not found
        """
        models = await self.get_available_models()

        for model in models:
            if model.get("id") == model_id:
                return model

        return None

    def _calculate_cost(self, response_data: Dict[str, Any], tokens: int) -> float:
        """
        Calculate cost based on response data.

        Args:
            response_data: API response data
            tokens: Total tokens used

        Returns:
            Estimated cost in USD
        """
        # OpenRouter may include cost in response
        if "usage" in response_data:
            usage = response_data["usage"]
            if "cost" in usage:
                return float(usage["cost"])

        # Fallback: estimate based on tokens (rough estimate)
        # This will vary by model
        cost_per_token = 0.00001  # Very rough estimate
        return tokens * cost_per_token

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("OpenRouter client closed")
