"""Уровень 3 - conmponent."""

from .base import BaseC4Element as _BaseC4Element
from .base import BaseSprite as _BaseSprite
from .tag import ElementTag as _ElementTag


class BaseComponent(_BaseC4Element):
    """BaseComponent."""

    def __init__(
        self: "BaseComponent",
        label: str,
        techn: str | None,
        descr: str | None,
        sprite: _BaseSprite | None,
        tags: tuple[_ElementTag, ...] | None,
        link: str | None,
    ) -> None:
        """Создать BaseComponent."""
        super().__init__(
            label=label,
            sprite=sprite,
            link=link,
            tags=tags,
        )
        self.__techn = techn
        self.__descr = descr

    @property
    def _repr_inside_pths(self: "BaseComponent") -> str:
        """Возвращает содержимое внутри скобок."""
        return "({alias}{label}{techn}{descr}{sprite}{tags}{link})\n".format(
            alias=self.format_alias,
            label=self._format_label,
            techn=self._repr_if_not_none("techn", self.__techn),
            descr=self._repr_if_not_none("descr", self.__descr),
            sprite=self._format_sprite,
            tags=self._format_tags,
            link=self._format_link,
        )

    def __repr__(self: "BaseComponent") -> str:
        """Return string representation."""
        raise NotImplementedError("Метод не переопределен")


class Component(BaseComponent):
    """Component."""

    def __init__(
        self: "Component",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать Component."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "Component") -> str:
        """Return string representation."""
        return f"Component{self._repr_inside_pths}"


class ComponentDb(BaseComponent):
    """ComponentDb."""

    def __init__(
        self: "ComponentDb",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать ComponentDb."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "ComponentDb") -> str:
        """Return string representation."""
        return f"ComponentDb{self._repr_inside_pths}"


class ComponentQueue(BaseComponent):
    """ComponentQueue."""

    def __init__(
        self: "ComponentQueue",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать ComponentQueue."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "ComponentQueue") -> str:
        """Return string representation."""
        return f"ComponentQueue{self._repr_inside_pths}"


class ComponentExt(BaseComponent):
    """ComponentExt."""

    def __init__(
        self: "ComponentExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать ComponentExt."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "ComponentExt") -> str:
        """Return string representation."""
        return f"Component_Ext{self._repr_inside_pths}"


class ComponentDbExt(BaseComponent):
    """ComponentDbExt."""

    def __init__(
        self: "ComponentDbExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать ComponentDbExt."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "ComponentDbExt") -> str:
        """Return string representation."""
        return f"ComponentDb_Ext{self._repr_inside_pths}"


class ComponentQueueExt(BaseComponent):
    """ComponentDbExt."""

    def __init__(
        self: "ComponentQueueExt",
        label: str,
        techn: str = "",
        descr: str = "",
        sprite: _BaseSprite | None = None,
        tags: tuple[_ElementTag, ...] | None = None,
        link: str | None = None,
    ) -> None:
        """Создать ComponentQueueExt."""
        super().__init__(
            label=label,
            techn=techn,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
        )

    def __repr__(self: "ComponentQueueExt") -> str:
        """Return string representation."""
        return f"ComponentQueue_Ext{self._repr_inside_pths}"
