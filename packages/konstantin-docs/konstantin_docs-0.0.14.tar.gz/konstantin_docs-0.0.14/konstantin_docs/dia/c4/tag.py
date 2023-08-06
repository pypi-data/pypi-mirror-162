"""Поддержка тегов."""

from .base import BaseSprite as _BaseSprite
from .base import BaseTag as _BaseTag


class ElementTag(_BaseTag):
    """Тег для элементов."""

    __bg_color: str | None
    __font_color: str | None
    __border_color: str | None

    def __init__(
        self: "ElementTag",
        tag_stereo: str,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
    ) -> None:
        """Создает тег для элементов."""
        super().__init__(tag_stereo)
        self.__bg_color = bg_color
        self.__font_color = font_color
        self.__border_color = border_color

    def repr_declaration(self: "ElementTag") -> str:
        """Объявление тега в начале файла."""
        return (
            f'AddElementTag("{self.repr_tag()}"'
            f"{self._repr_font_color()}"
            f"{self._repr_border_color()}"
            ")"
        )

    def _repr_border_color(self: "ElementTag") -> str:
        if self.__border_color is None:
            return ""
        return f', $borderColor="{self.__border_color}"'

    def _repr_font_color(self: "ElementTag") -> str:
        if self.__font_color is None:
            return ""
        return f', $fontColor="{self.__font_color}"'


class RelTag(_BaseTag):
    """Тег для отношений."""

    def __init__(
        self: "RelTag",
        tag_stereo: str,
        text_color: str | None = None,
        line_color: str | None = None,
        line_style: str | None = None,
        sprite: _BaseSprite | None = None,
        techn: str | None = None,
        legent_text: str | None = None,
        legend_sprite: str | None = None,
    ) -> None:
        """Создает тег для отношений."""
        super().__init__(tag_stereo)
        self.__text_color = text_color
        self.__line_color = line_color
        self.__line_style = line_style

    def repr_declaration(self: "RelTag") -> str:
        """Объявление тега в начале файла."""
        return (
            f'AddRelTag("{self.repr_tag()}"'
            f"{self._repr_if_not_none(self.__text_color, 'textColor')}"
            f"{self._repr_if_not_none(self.__line_color, 'lineColor')}"
            f"{self._repr_if_not_none(self.__line_style, 'lineStyle')}"
            ")"
        )
