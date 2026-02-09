"""
Генератор адаптивных заданий.
"""
import json
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DifficultyLevel, LearningStyle, ScaffoldingLevel, Subject
from app.core.exceptions import NotFoundException
from app.models.student import Student, StudentProfile
from app.models.task import Task
from app.schemas.generation import (
    GeneratedTask,
    GenerationExplanation,
    TaskAdaptations,
    TaskContent,
)
from app.services.generation.adapters import compute_adaptations
from app.services.generation.llm_client import get_llm_client
from app.services.generation.prompts import (
    DIFFICULTY_NAMES,
    DISABILITY_PROMPTS,
    LEARNING_STYLE_NAMES,
    PROMPT_EXPLAIN_RECOMMENDATION,
    PROMPT_GENERATE_FEEDBACK,
    PROMPT_GENERATE_TASK,
    SCAFFOLDING_NAMES,
    SUBJECT_NAMES,
    SYSTEM_PROMPT_TASK_GENERATOR,
)
from app.services.student import StudentService


class TaskGenerator:
    """Генератор адаптивных заданий."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_client()

    async def _get_student_with_profile(self, student_id: int) -> tuple[Student, StudentProfile]:
        """Получить ученика с профилем."""
        service = StudentService(self.db)
        student = await service.get_by_id(student_id)

        if not student.profile:
            raise NotFoundException("Профиль ученика не найден")

        return student, student.profile

    def _build_disability_context(self, disability_types: list[str]) -> str:
        """Собрать контекст по типам ОВЗ."""
        contexts = []
        for dt in disability_types:
            if dt in DISABILITY_PROMPTS:
                contexts.append(DISABILITY_PROMPTS[dt])
        return "\n".join(contexts) if contexts else "Без особых требований"

    async def generate_task(
        self,
        student_id: int,
        subject: Subject,
        topic: str,
        difficulty: DifficultyLevel | None = None,
        iep_goal_id: int | None = None,
    ) -> GeneratedTask:
        """
        Сгенерировать адаптивное задание для ученика.

        Args:
            student_id: ID ученика
            subject: Предмет
            topic: Тема
            difficulty: Уровень сложности (авто, если None)
            iep_goal_id: ID цели ИОП (опционально)

        Returns:
            Сгенерированное задание
        """
        student, profile = await self._get_student_with_profile(student_id)

        # Определяем сложность автоматически, если не указана
        if difficulty is None:
            difficulty = profile.current_difficulty

        # Собираем параметры для промпта
        disabilities = profile.disability_types or []
        disability_context = self._build_disability_context(disabilities)

        prompt = PROMPT_GENERATE_TASK.format(
            grade=student.grade,
            disabilities=", ".join(disabilities) if disabilities else "нет",
            learning_style=LEARNING_STYLE_NAMES.get(
                profile.learning_style, profile.learning_style
            ),
            current_difficulty=DIFFICULTY_NAMES.get(
                profile.current_difficulty.value if profile.current_difficulty else 3, "Средний"
            ),
            scaffolding_level=SCAFFOLDING_NAMES.get(
                profile.scaffolding_level.value if profile.scaffolding_level else 3, "Средняя поддержка"
            ),
            subject=SUBJECT_NAMES.get(subject, subject),
            topic=topic,
            difficulty=DIFFICULTY_NAMES.get(difficulty.value, "Средний"),
        )

        # Добавляем контекст по ОВЗ
        full_system = SYSTEM_PROMPT_TASK_GENERATOR + "\n\n" + disability_context

        # Генерируем через LLM
        response = await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=full_system,
            temperature=0.7,
        )

        # Вычисляем адаптации
        adaptations_result = compute_adaptations(
            disability_types=disabilities,
            learning_style=LearningStyle(profile.learning_style) if profile.learning_style else None,
            scaffolding_level=ScaffoldingLevel(profile.scaffolding_level) if profile.scaffolding_level else None,
            profile_settings={
                "font_size": profile.font_size,
                "line_height": profile.line_height,
                "color_scheme": profile.color_scheme,
                "audio_enabled": profile.audio_enabled,
            },
        )

        # Формируем результат
        content = TaskContent(
            type=response.get("type", "multiple_choice"),
            question=response.get("question", ""),
            options=response.get("options"),
            correct_answer=response.get("correct_answer"),
            hints=response.get("hints", []),
            explanation=response.get("explanation"),
        )

        adaptations = TaskAdaptations(
            font_size=adaptations_result.font_size,
            line_height=adaptations_result.line_height,
            simplified_text=adaptations_result.simplified_text,
            audio_enabled=adaptations_result.audio_enabled,
            extra_time=adaptations_result.extra_time,
            scaffolding_level=adaptations_result.scaffolding_level,
        )

        return GeneratedTask(
            title=response.get("title", f"Задание по теме: {topic}"),
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            content=content,
            adaptations=adaptations,
            generation_metadata={
                "model": self.llm.default_model,
                "generated_at": datetime.now(UTC).isoformat(),
                "reasoning": response.get("reasoning", ""),
                "student_profile": {
                    "grade": student.grade,
                    "disabilities": disabilities,
                    "learning_style": profile.learning_style,
                    "scaffolding_level": profile.scaffolding_level.value if profile.scaffolding_level else 3,
                },
                "adaptations_applied": adaptations_result.to_dict(),
            },
        )

    async def adapt_existing_task(
        self,
        task: Task,
        student_id: int,
    ) -> dict:
        """
        Адаптировать существующее задание под профиль ученика.

        Args:
            task: Существующее задание
            student_id: ID ученика для адаптации

        Returns:
            Словарь с адаптациями
        """
        student, profile = await self._get_student_with_profile(student_id)
        disabilities = profile.disability_types or []

        # Вычисляем адаптации
        adaptations_result = compute_adaptations(
            disability_types=disabilities,
            learning_style=LearningStyle(profile.learning_style) if profile.learning_style else None,
            scaffolding_level=ScaffoldingLevel(profile.scaffolding_level) if profile.scaffolding_level else None,
            profile_settings={
                "font_size": profile.font_size,
                "line_height": profile.line_height,
                "color_scheme": profile.color_scheme,
                "audio_enabled": profile.audio_enabled,
            },
        )

        return {
            "original_task_id": task.id,
            "student_id": student_id,
            "adaptations": adaptations_result.to_dict(),
            "adapted_at": datetime.now(UTC).isoformat(),
        }

    async def explain_recommendation(
        self,
        student_id: int,
        task_info: dict,
        progress_history: list[dict] | None = None,
    ) -> GenerationExplanation:
        """
        Объяснить рекомендацию задания (XAI).

        Args:
            student_id: ID ученика
            task_info: Информация о задании
            progress_history: История прогресса

        Returns:
            Объяснение рекомендации
        """
        student, profile = await self._get_student_with_profile(student_id)

        student_profile_str = json.dumps({
            "grade": student.grade,
            "disabilities": profile.disability_types,
            "learning_style": profile.learning_style,
            "current_difficulty": profile.current_difficulty.value if profile.current_difficulty else 3,
            "scaffolding_level": profile.scaffolding_level.value if profile.scaffolding_level else 3,
        }, ensure_ascii=False, indent=2)

        prompt = PROMPT_EXPLAIN_RECOMMENDATION.format(
            student_profile=student_profile_str,
            task_info=json.dumps(task_info, ensure_ascii=False, indent=2),
            progress_history=json.dumps(progress_history or [], ensure_ascii=False, indent=2),
        )

        response = await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_TASK_GENERATOR,
            temperature=0.5,
        )

        return GenerationExplanation(
            reasoning=response.get("reasoning", "Объяснение недоступно"),
            factors=response.get("factors", []),
            student_profile_considered={
                "grade": student.grade,
                "disabilities": profile.disability_types,
                "learning_style": profile.learning_style,
            },
            alternative_suggestions=response.get("next_steps", []),
        )

    async def generate_feedback(
        self,
        task_title: str,
        correct_answer: str,
        student_answer: str,
        is_correct: bool,
        hints_used: int,
        time_spent: int | None,
        student_id: int,
    ) -> dict:
        """
        Сгенерировать персонализированную обратную связь.

        Args:
            task_title: Название задания
            correct_answer: Правильный ответ
            student_answer: Ответ ученика
            is_correct: Правильный ли ответ
            hints_used: Количество использованных подсказок
            time_spent: Время выполнения в секундах
            student_id: ID ученика

        Returns:
            Словарь с обратной связью
        """
        student, profile = await self._get_student_with_profile(student_id)
        disabilities = profile.disability_types or []

        prompt = PROMPT_GENERATE_FEEDBACK.format(
            task_title=task_title,
            correct=correct_answer,
            student_answer=student_answer,
            hints_used=hints_used,
            time_spent=f"{time_spent} сек." if time_spent else "не указано",
            disabilities=", ".join(disabilities) if disabilities else "нет",
            current_level=DIFFICULTY_NAMES.get(
                profile.current_difficulty.value if profile.current_difficulty else 3, "Средний"
            ),
        )

        response = await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_TASK_GENERATOR,
            temperature=0.7,
        )

        return {
            "message": response.get("message", "Хорошая работа!" if is_correct else "Попробуй ещё раз!"),
            "detailed": response.get("detailed", ""),
            "encouragement": response.get("encouragement", "Продолжай в том же духе!"),
            "tip": response.get("tip", ""),
            "is_correct": is_correct,
        }
