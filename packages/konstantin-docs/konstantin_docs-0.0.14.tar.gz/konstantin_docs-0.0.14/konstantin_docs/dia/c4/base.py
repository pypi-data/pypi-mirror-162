"""Базовые классы."""

from enum import Enum


class BaseTag:
    """Базовый класс для тегов."""

    def __init__(
        self: "BaseTag",
        tag_stereo: str,
    ) -> None:
        """Create base tag."""
        self.__tagStereo = tag_stereo

    @staticmethod
    def _repr_if_not_none(
        value: str | None,
        text: str,
    ) -> str:
        if value is None:
            return ""
        return f', ${text}="{value}"'

    def repr_declaration(self: "BaseTag") -> str:
        """Объявление тега в начале файла."""
        raise NotImplementedError("Метод не переопределен.")

    def repr_func_param(self: "BaseTag") -> str:
        """Представление тега для параметра функции."""
        return f'$tags="{self.__tagStereo}"'

    def repr_tag(self: "BaseTag") -> str:
        """Только имя тега."""
        return f"{self.__tagStereo}"


class BaseSprites(Enum):
    """Базовая библиотека."""


class BaseSprite:
    """Базовый класс для изображений."""

    def __init__(
        self: "BaseSprite",
        common: str,
        common_sprite: str,
        sprite: BaseSprites,
    ) -> None:
        """Create base sprite."""
        self.__common = common
        self.__common_sprite = common_sprite
        self.__sprite = sprite

    @property
    def common(self: "BaseSprite") -> str:
        """Общая библиотека для импорта."""
        return f"!include <{self.__common}>"

    @property
    def sprite_full(self: "BaseSprite") -> str:
        """Импорт спрайта."""
        return f"!include <{self.__common_sprite}/{self.__sprite.value}>"

    @property
    def sprite_short(self: "BaseSprite") -> str:
        """Импорт спрайта."""
        return self.__sprite.value


class BaseC4Element:
    """Базовый элемент диаграмм."""

    def __init__(
        self: "BaseC4Element",
        label: str,
        sprite: BaseSprite | None,
        link: str | None,
        tags: tuple[BaseTag] | None,
    ) -> None:
        """Create BaseC4Element."""
        self.__alias = str(id(self)).replace("-", "_")
        self.__label = label
        self.__sprite = sprite
        self.__link = link
        self.__tags = tags

    @property
    def all_sprites(self: "BaseC4Element") -> list[BaseSprite]:
        """Возвращает все спрайты."""
        sprites: list[BaseSprite] = []
        if self.__sprite is not None:
            sprites.append(self.__sprite or None)
        return sprites

    @property
    def all_tags(self: "BaseC4Element") -> list[BaseTag]:
        """Возвращает список всех тегов."""
        tags: list[BaseTag] = []
        tags.extend(self.__tags or [])
        return tags

    @property
    def format_alias(self: "BaseC4Element") -> str:
        """Возвращает alias."""
        return self.__alias

    @property
    def _format_label(self: "BaseC4Element") -> str:
        """Представление для label."""
        return self._repr_if_not_none("label", self.__label)

    @property
    def _format_link(self: "BaseC4Element") -> str:
        """Ссылка."""
        return self._repr_if_not_none("link", self.__link)

    @property
    def _format_sprite(self: "BaseC4Element") -> str:
        """Представление для спрайтов."""
        if self.__sprite is None:
            return ""
        # return self.__sprite.sprite_short
        return self._repr_if_not_none("sprite", self.__sprite.sprite_short)

    @property
    def _format_tags(self: "BaseC4Element") -> str:
        """Тег."""
        if self.__tags is None:
            return ""
        return f', $tags="{"+".join([t.repr_tag() for t in self.__tags])}"'

    @staticmethod
    def _repr_if_not_none(
        text: str,
        value: str | None,
    ) -> str:
        if value is None:
            return ""
        return f', ${text}="{value}"'


class BaseRelation:
    """Базовый класс для отношений."""

    def __init__(
        self: "BaseRelation",
        kind: str,
        links: tuple[BaseC4Element, BaseC4Element],
        label: str,
        techn: str,
        descr: str,
        link: str | None,
        tags: tuple[BaseTag, ...] | None,
    ) -> None:
        """Создает Relation."""
        self.__kind = kind
        self.__links = links
        self.__label = label
        self.__techn = techn
        self.__descr = descr
        self.__link = link
        self.__tags = tags

    @property
    def _repr_link(self: "BaseRelation") -> str:
        """Представление ссылки."""
        if self.__link is None:
            return ""
        return f', $link="{self.__link}"'

    @property
    def repr_tags(self: "BaseRelation") -> str:
        """Тег."""
        if self.__tags is None:
            return ""
        return f', $tags="{"+".join([t.repr_tag() for t in self.__tags])}"'

    @property
    def all_tags(self: "BaseRelation") -> list[BaseTag]:
        """Возвращает список всех тегов."""
        tags: list[BaseTag] = []
        if self.__tags is not None:
            tags.extend(self.__tags)
        return tags

    def __repr__(self: "BaseRelation") -> str:
        """Return string representation."""
        template = """
{kind}({link_from}, {link_to}, "{label}", "{techn}", "{descr}"{link}{tags})"""
        return template.format(
            kind=self.__kind,
            link_from=self.__links[0].format_alias,
            link_to=self.__links[1].format_alias,
            label=self.__label,
            techn=self.__techn,
            descr=self.__descr,
            link=self._repr_link,
            tags=self.repr_tags,
        )
