"""Уровень 2 - container."""

from .base import BaseC4Element as _BaseC4Element
from .base import BaseSprite as _BaseSprite
from .base import BaseTag as _BaseTag
from .component import BaseComponent as _BaseComponent
from .tag import ElementTag as _ElementTag


class BaseContainer(_BaseC4Element):
    """BaseContainer."""

    def __init__(
        self: "BaseContainer",
        label: str,
        techn: str | None,
        descr: str | None,
        sprite: _BaseSprite | None,
        tags: tuple[_ElementTag, ...] | None,
        link: str | None,
        links_component: list[_BaseComponent] | None,
    ) -> None:
        """Создать BaseContainer."""
        super().__init__(
            label=label,
            sprite=sprite,
            link=link,
            tags=tags,
        )
        self.__techn = techn
        self.__descr = descr
        self.__links_component = links_component

    @property
    def _format_links_component(self: "BaseContainer") -> str:
        """Возвращает список вложенных компонентов в виде строки."""
        if self.__links_component is None:
            return ""
        links_component_str = "".join(
            [repr(component) for component in self.__links_component],
        )
        return f"{{\n\t{links_component_str}\n}}"

    @property
    def _repr_inside_pths(self: "BaseContainer") -> str:
        """Возвращает содержимое внутри скобок + вложенные компоненты."""
        return (
            "({alias}{label}{techn}{descr}{sprite}{tags}{link})"
            "{links_component}\n"
        ).format(
            alias=self.format_alias,
            label=self._format_label,
            techn=self._repr_if_not_none("techn", self.__techn),
            descr=self._repr_if_not_none("descr", self.__descr),
            sprite=self._format_sprite,
            tags=self._format_tags,
            link=self._format_link,
            links_component=self._format_links_component,
        )

    @_BaseC4Element.all_sprites.getter
    def all_sprites(self: "BaseContainer") -> list[_BaseSprite]:
        """Возвращает все спрайты."""
        sprites: list[_BaseSprite] = []
        sprites = super().all_sprites
        sprites.extend(
            [
                sprites
                for link in self.__links_component or []
                for sprites in link.all_sprites
            ],
        )
        return sprites

    @_BaseC4Element.all_tags.getter
    def all_tags(self: "BaseContainer") -> list[_BaseTag]:
        """Возвращает все теги."""
        tags: list[_BaseTag] = []
        tags = super().all_tags
        tags.extend(
            [
                tags
                for link in self.__links_component or []
                for tags in link.all_tags
            ],
        )
        return tags

    def __repr__(self: "BaseContainer") -> str:
        """Return string representation."""
        raise NotImplementedError("Метод не переопределен")


class Container(BaseContainer):
    """Container."""

    def __init__(
        self: "Container",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать Container."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "Container") -> str:
        """Return string representation."""
        return f"Container{self._repr_inside_pths}"


class ContainerDb(BaseContainer):
    """ContainerDb."""

    def __init__(
        self: "ContainerDb",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerDb."""
        super().__init__(
            label=label,
            descr=descr,
            techn=techn,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerDb") -> str:
        """Return string representation."""
        return f"ContainerDb{self._repr_inside_pths}"


class ContainerQueue(BaseContainer):
    """ContainerQueue."""

    def __init__(
        self: "ContainerQueue",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerQueue."""
        super().__init__(
            label=label,
            descr=descr,
            techn=techn,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerQueue") -> str:
        """Return string representation."""
        return f"ContainerQueue{self._repr_inside_pths}"


class ContainerExt(BaseContainer):
    """ContainerExt."""

    def __init__(
        self: "ContainerExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerExt."""
        super().__init__(
            label=label,
            descr=descr,
            techn=techn,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerExt") -> str:
        """Return string representation."""
        return f"Container_Ext{self._repr_inside_pths}"


class ContainerDbExt(BaseContainer):
    """ContainerDbExt."""

    def __init__(
        self: "ContainerDbExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerDbExt."""
        super().__init__(
            label=label,
            descr=descr,
            techn=techn,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerDbExt") -> str:
        """Return string representation."""
        return f"ContainerDb_Ext{self._repr_inside_pths}"


class ContainerQueueExt(BaseContainer):
    """ContainerQueueExt."""

    def __init__(
        self: "ContainerQueueExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerQueueExt."""
        super().__init__(
            label=label,
            descr=descr,
            techn=techn,
            sprite=sprite,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerQueueExt") -> str:
        """Return string representation."""
        return f"ContainerQueue_Ext{self._repr_inside_pths}"


class ContainerBoundary(BaseContainer):
    """ContainerBoundary."""

    def __init__(
        self: "ContainerBoundary",
        label: str,
        tags: tuple[_ElementTag] | None = None,
        link: str | None = None,
        links_component: list[_BaseComponent] | None = None,
    ) -> None:
        """Создать ContainerBoundary."""
        super().__init__(
            label=label,
            descr=None,
            techn=None,
            sprite=None,
            link=link,
            tags=tags,
            links_component=links_component,
        )

    def __repr__(self: "ContainerBoundary") -> str:
        """Return string representation."""
        return f"Container_Boundary{self._repr_inside_pths}"
