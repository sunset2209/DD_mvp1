"""
Адаптеры для разных типов ОВЗ.
Применяют специфические адаптации к заданиям.
"""
from app.core.constants import DisabilityType, LearningStyle, ScaffoldingLevel


class TaskAdaptationResult:
    """Результат адаптации задания."""

    def __init__(self):
        self.font_size: int = 16
        self.line_height: float = 1.5
        self.color_scheme: str = "default"
        self.simplified_text: bool = False
        self.audio_enabled: bool = False
        self.extra_time: int = 0
        self.scaffolding_level: int = 3
        self.visual_supports: list[str] = []
        self.audio_supports: list[str] = []
        self.interaction_modifications: list[str] = []
        self.content_modifications: list[str] = []

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        return {
            "font_size": self.font_size,
            "line_height": self.line_height,
            "color_scheme": self.color_scheme,
            "simplified_text": self.simplified_text,
            "audio_enabled": self.audio_enabled,
            "extra_time": self.extra_time,
            "scaffolding_level": self.scaffolding_level,
            "visual_supports": self.visual_supports,
            "audio_supports": self.audio_supports,
            "interaction_modifications": self.interaction_modifications,
            "content_modifications": self.content_modifications,
        }


class BaseAdapter:
    """Базовый адаптер."""

    def apply(self, result: TaskAdaptationResult) -> None:
        """Применить адаптации."""
        pass


class DyslexiaAdapter(BaseAdapter):
    """Адаптер для дислексии."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.font_size = max(result.font_size, 18)
        result.line_height = max(result.line_height, 1.8)
        result.audio_enabled = True
        result.extra_time += 30  # +30% времени
        result.content_modifications.extend([
            "Использовать простые короткие предложения",
            "Избегать сложных буквосочетаний",
            "Разбить текст на абзацы по 2-3 предложения",
        ])
        result.audio_supports.append("Озвучивание всего текста задания")


class DyscalculiaAdapter(BaseAdapter):
    """Адаптер для дискалькулии."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.extra_time += 50  # +50% времени для математики
        result.visual_supports.extend([
            "Числовая линейка",
            "Визуализация чисел объектами",
            "Пошаговый разбор вычислений",
        ])
        result.content_modifications.extend([
            "Разбить задачу на мелкие шаги",
            "Использовать наглядные примеры",
            "Избегать абстрактных чисел",
        ])


class DysgraphiaAdapter(BaseAdapter):
    """Адаптер для дисграфии."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.interaction_modifications.extend([
            "Предпочитать выбор из вариантов",
            "Минимизировать письменный ввод",
            "Добавить голосовой ввод",
        ])
        result.content_modifications.append(
            "Заменить открытые вопросы на выбор из вариантов"
        )


class ADHDAdapter(BaseAdapter):
    """Адаптер для СДВГ."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.visual_supports.extend([
            "Визуальный таймер",
            "Прогресс-бар выполнения",
            "Яркие акценты на ключевых элементах",
        ])
        result.interaction_modifications.extend([
            "Разбить на короткие этапы",
            "Немедленная обратная связь",
            "Интерактивные элементы",
        ])
        result.content_modifications.append(
            "Короткие задания по 5-7 минут"
        )


class ASDAdapter(BaseAdapter):
    """Адаптер для РАС."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.visual_supports.extend([
            "Чёткая визуальная структура",
            "Пошаговые инструкции с картинками",
            "Предсказуемый порядок элементов",
        ])
        result.content_modifications.extend([
            "Избегать метафор и идиом",
            "Конкретные однозначные формулировки",
            "Предупреждение о переходах",
        ])


class HearingImpairedAdapter(BaseAdapter):
    """Адаптер для нарушений слуха."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.audio_enabled = False  # Отключаем аудио по умолчанию
        result.visual_supports.extend([
            "Субтитры для всего аудио",
            "Визуальные инструкции",
            "Анимации вместо аудио",
        ])
        result.content_modifications.append(
            "Заменить аудио на визуальные элементы"
        )


class VisualImpairedAdapter(BaseAdapter):
    """Адаптер для нарушений зрения."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.font_size = max(result.font_size, 24)
        result.line_height = max(result.line_height, 2.0)
        result.color_scheme = "high_contrast"
        result.audio_enabled = True
        result.audio_supports.extend([
            "Полное аудиоописание",
            "Совместимость со скринридером",
        ])
        result.content_modifications.append(
            "Описывать все визуальные элементы текстом"
        )


class IntellectualDisabilityAdapter(BaseAdapter):
    """Адаптер для интеллектуальных нарушений."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.simplified_text = True
        result.font_size = max(result.font_size, 20)
        result.extra_time += 100  # +100% времени
        result.content_modifications.extend([
            "Максимально простой язык",
            "Много повторений",
            "Наглядные примеры из жизни",
            "Мельчайшие шаги",
        ])
        result.visual_supports.append("Картинки для каждого шага")


class MotorDisabilityAdapter(BaseAdapter):
    """Адаптер для двигательных нарушений."""

    def apply(self, result: TaskAdaptationResult) -> None:
        result.extra_time += 30
        result.interaction_modifications.extend([
            "Крупные кликабельные элементы",
            "Возможность навигации клавиатурой",
            "Голосовое управление",
        ])


# Маппинг типов ОВЗ на адаптеры
DISABILITY_ADAPTERS: dict[str, type[BaseAdapter]] = {
    DisabilityType.DYSLEXIA: DyslexiaAdapter,
    DisabilityType.DYSCALCULIA: DyscalculiaAdapter,
    DisabilityType.DYSGRAPHIA: DysgraphiaAdapter,
    DisabilityType.ADHD: ADHDAdapter,
    DisabilityType.ASD: ASDAdapter,
    DisabilityType.HEARING_IMPAIRED: HearingImpairedAdapter,
    DisabilityType.VISUAL_IMPAIRED: VisualImpairedAdapter,
    DisabilityType.INTELLECTUAL: IntellectualDisabilityAdapter,
    DisabilityType.MOTOR: MotorDisabilityAdapter,
}


def apply_learning_style_adaptations(
    result: TaskAdaptationResult,
    learning_style: LearningStyle,
) -> None:
    """Применить адаптации на основе стиля обучения."""
    if learning_style == LearningStyle.VISUAL:
        result.visual_supports.extend([
            "Схемы и диаграммы",
            "Цветовое кодирование",
            "Инфографика",
        ])
    elif learning_style == LearningStyle.AUDITORY:
        result.audio_enabled = True
        result.audio_supports.extend([
            "Озвучивание текста",
            "Аудио-инструкции",
            "Музыкальное сопровождение",
        ])
    elif learning_style == LearningStyle.KINESTHETIC:
        result.interaction_modifications.extend([
            "Drag-and-drop элементы",
            "Интерактивные манипуляции",
            "Практические задания",
        ])
    elif learning_style == LearningStyle.READING:
        result.content_modifications.extend([
            "Подробные текстовые инструкции",
            "Возможность записи ответов",
        ])


def apply_scaffolding_level(
    result: TaskAdaptationResult,
    scaffolding_level: ScaffoldingLevel,
) -> None:
    """Применить уровень скэффолдинга."""
    result.scaffolding_level = scaffolding_level.value

    if scaffolding_level == ScaffoldingLevel.FULL_SUPPORT:
        result.content_modifications.extend([
            "Пошаговые инструкции для каждого действия",
            "Автоматические подсказки",
            "Демонстрация правильного ответа",
        ])
    elif scaffolding_level == ScaffoldingLevel.HIGH_SUPPORT:
        result.content_modifications.extend([
            "Подробные подсказки по запросу",
            "Частичная подсказка ответа",
        ])
    elif scaffolding_level == ScaffoldingLevel.MEDIUM_SUPPORT:
        result.content_modifications.append(
            "Базовые подсказки доступны"
        )
    elif scaffolding_level == ScaffoldingLevel.LOW_SUPPORT:
        result.content_modifications.append(
            "Минимальные подсказки только при ошибках"
        )
    # INDEPENDENT - без дополнительных модификаций


def compute_adaptations(
    disability_types: list[str],
    learning_style: LearningStyle | None = None,
    scaffolding_level: ScaffoldingLevel | None = None,
    profile_settings: dict | None = None,
) -> TaskAdaptationResult:
    """
    Вычислить комплексные адаптации на основе профиля ученика.

    Args:
        disability_types: Список типов ОВЗ
        learning_style: Стиль обучения
        scaffolding_level: Уровень скэффолдинга
        profile_settings: Дополнительные настройки из профиля

    Returns:
        TaskAdaptationResult с всеми адаптациями
    """
    result = TaskAdaptationResult()

    # Применяем настройки из профиля
    if profile_settings:
        result.font_size = profile_settings.get("font_size", 16)
        result.line_height = profile_settings.get("line_height", 1.5)
        result.color_scheme = profile_settings.get("color_scheme", "default")
        result.audio_enabled = profile_settings.get("audio_enabled", False)

    # Применяем адаптеры для каждого типа ОВЗ
    for disability_type in disability_types:
        adapter_class = DISABILITY_ADAPTERS.get(disability_type)
        if adapter_class:
            adapter = adapter_class()
            adapter.apply(result)

    # Применяем адаптации стиля обучения
    if learning_style:
        apply_learning_style_adaptations(result, learning_style)

    # Применяем уровень скэффолдинга
    if scaffolding_level:
        apply_scaffolding_level(result, scaffolding_level)

    return result
