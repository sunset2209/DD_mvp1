"""Generation сервисы для работы с LLM."""

from app.services.generation.adapters import compute_adaptations
from app.services.generation.generator import TaskGenerator
from app.services.generation.llm_client import LLMClient, get_llm_client

__all__ = [
    "LLMClient",
    "TaskGenerator",
    "compute_adaptations",
    "get_llm_client",
]
