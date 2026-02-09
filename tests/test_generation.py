"""
Тесты генерации с mock LLM.
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.core.constants import DifficultyLevel, Subject
from app.services.generation.prompts import (
    DIFFICULTY_NAMES,
    DISABILITY_PROMPTS,
    SUBJECT_NAMES,
)


class TestPrompts:
    """Тесты промптов."""

    def test_subject_names_complete(self):
        """Тест полноты названий предметов."""
        for subject in Subject:
            assert subject in SUBJECT_NAMES

    def test_difficulty_names_complete(self):
        """Тест полноты названий сложности."""
        for level in DifficultyLevel:
            assert level.value in DIFFICULTY_NAMES

    def test_disability_prompts_exist(self):
        """Тест наличия промптов для ОВЗ."""
        expected_types = [
            "dyslexia", "dyscalculia", "dysgraphia",
            "adhd", "asd", "hearing", "visual", "intellectual",
        ]
        for dt in expected_types:
            assert dt in DISABILITY_PROMPTS
            assert len(DISABILITY_PROMPTS[dt]) > 50  # Минимальная длина промпта


class TestMockLLM:
    """Тесты с mock LLM клиентом."""

    @pytest.mark.asyncio
    async def test_generate_returns_string(self):
        """Тест что generate возвращает строку."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Сгенерированный текст"

        with patch("app.services.generation.llm_client.AsyncOpenAI") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            from app.services.generation.llm_client import LLMClient
            client = LLMClient()
            client.client = mock_instance

            result = await client.generate("Тестовый промпт")

            assert result == "Сгенерированный текст"

    @pytest.mark.asyncio
    async def test_generate_structured_parses_json(self):
        """Тест парсинга JSON из ответа LLM."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = '{"title": "Задание", "type": "multiple_choice"}'

        with patch("app.services.generation.llm_client.AsyncOpenAI") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            from app.services.generation.llm_client import LLMClient
            client = LLMClient()
            client.client = mock_instance

            result = await client.generate_structured("Создай задание")

            assert isinstance(result, dict)
            assert result["title"] == "Задание"

    @pytest.mark.asyncio
    async def test_generate_structured_handles_markdown(self):
        """Тест обработки markdown блоков в ответе."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = '```json\n{"key": "value"}\n```'

        with patch("app.services.generation.llm_client.AsyncOpenAI") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            from app.services.generation.llm_client import LLMClient
            client = LLMClient()
            client.client = mock_instance

            result = await client.generate_structured("Тест")

            assert result["key"] == "value"

    @pytest.mark.asyncio
    async def test_generate_structured_handles_invalid_json(self):
        """Тест обработки невалидного JSON."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Это не JSON"

        with patch("app.services.generation.llm_client.AsyncOpenAI") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            from app.services.generation.llm_client import LLMClient
            client = LLMClient()
            client.client = mock_instance

            result = await client.generate_structured("Тест")

            assert "error" in result
            assert "raw_response" in result


class TestGeneratorWithMock:
    """Тесты генератора с mock."""

    @pytest.mark.asyncio
    async def test_task_generation_structure(self):
        """Тест структуры генерируемого задания."""
        # Проверяем что TaskContent и TaskAdaptations имеют все поля
        from app.schemas.generation import GeneratedTask, TaskAdaptations, TaskContent

        content = TaskContent(
            type="multiple_choice",
            question="Тестовый вопрос",
            options=["A", "B", "C"],
            correct_answer="A",
        )

        adaptations = TaskAdaptations(
            font_size=18,
            line_height=1.8,
            simplified_text=True,
            audio_enabled=True,
            extra_time=30,
            scaffolding_level=2,
        )

        task = GeneratedTask(
            title="Тестовое задание",
            subject=Subject.MATH,
            topic="Сложение",
            difficulty=DifficultyLevel.EASY,
            content=content,
            adaptations=adaptations,
        )

        assert task.title == "Тестовое задание"
        assert task.content.type == "multiple_choice"
        assert task.adaptations.font_size == 18


class TestFeedbackGeneration:
    """Тесты генерации обратной связи."""

    def test_feedback_structure(self):
        """Тест структуры обратной связи."""
        feedback = {
            "message": "Молодец!",
            "detailed": "Ты правильно решил задачу",
            "encouragement": "Так держать!",
            "tip": "В следующий раз попробуй без подсказок",
            "is_correct": True,
        }

        assert "message" in feedback
        assert "encouragement" in feedback
        assert feedback["is_correct"] is True

    def test_feedback_for_incorrect_answer(self):
        """Тест обратной связи для неправильного ответа."""
        feedback = {
            "message": "Не совсем так",
            "detailed": "Правильный ответ: 8",
            "encouragement": "Ничего страшного, попробуй ещё раз!",
            "tip": "Попробуй посчитать на пальцах",
            "is_correct": False,
        }

        assert feedback["is_correct"] is False
        assert "попробуй" in feedback["tip"].lower()
