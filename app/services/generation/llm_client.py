"""
Клиент для работы с OpenRouter LLM API.
"""
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()


class LLMClient:
    """Клиент для работы с LLM через OpenRouter."""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.default_model = settings.DEFAULT_LLM_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Сгенерировать текст через LLM.

        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт (опционально)
            model: Модель (по умолчанию claude-3-haiku)
            temperature: Температура генерации
            max_tokens: Максимум токенов

        Returns:
            Сгенерированный текст
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.5,
    ) -> dict:
        """
        Сгенерировать структурированный JSON ответ.

        Args:
            prompt: Промпт с инструкцией вернуть JSON
            system_prompt: Системный промпт
            model: Модель
            temperature: Температура

        Returns:
            Распарсенный JSON
        """
        import json

        full_system = (system_prompt or "") + "\nОтвечай только валидным JSON без markdown."

        response = await self.generate(
            prompt=prompt,
            system_prompt=full_system,
            model=model,
            temperature=temperature,
        )

        # Пытаемся распарсить JSON
        try:
            # Убираем возможные markdown блоки
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_response": response, "error": "Failed to parse JSON"}


# Singleton instance
llm_client = LLMClient()


def get_llm_client() -> LLMClient:
    """Получить экземпляр LLM клиента."""
    return llm_client
