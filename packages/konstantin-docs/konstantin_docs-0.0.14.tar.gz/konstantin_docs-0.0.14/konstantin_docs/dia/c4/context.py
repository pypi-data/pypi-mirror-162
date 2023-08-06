"""Уровень 1 - context."""

from .base import BaseC4Element as _BaseC4Element
from .base import BaseSprite
from .base import BaseTag
from .container import BaseContainer as _BaseContainer
from .tag import ElementTag as _ElementTag


class BaseContext(_BaseC4Element):
    """BaseContext."""

    __descr: str | None
    __boundary_type: str | None
    __links_container: list[_BaseContainer] | None

    def __init__(
        self: "BaseContext",
        label: str,
        descr: str | None,
        sprite: BaseSprite | None,
        link: str | None,
        tags: tuple[_ElementTag] | None,
        boundary_type: str | None,
        links_container: list[_BaseContainer] | None,
    ) -> None:
        """Создать BaseContext."""
        super().__init__(
            label=label,
            sprite=sprite,
            link=link,
            tags=tags,
        )
        self.__descr = descr
        self.__boundary_type = boundary_type
        self.__links_container = links_container

    @property
    def _format_links_container(self: "BaseContext") -> str:
        """Возвращает список вложенных контейнеров в виде строки."""
        if self.__links_container is None:
            return ""
        links_container_str: str = "".join(
            [repr(container) for container in self.__links_container],
        )
        return f"{{\n\t{links_container_str}\n}}"

    @property
    def _repr_inside_pths(self: "BaseContext") -> str:
        """Возвращает содержимое внутри скобок + вложенные контейнеры."""
        return (
            "({alias}{label}{descr}{sprite}{tags}{link}{type})"
            "{links_container}\n"
        ).format(
            alias=self.format_alias,
            label=self._format_label,
            descr=self._repr_if_not_none("descr", self.__descr),
            sprite=self._format_sprite,
            tags=self._format_tags,
            link=self._format_link,
            type=self._repr_if_not_none("type", self.__boundary_type),
            links_container=self._format_links_container,
        )

    @_BaseC4Element.all_sprites.getter
    def all_sprites(self: "BaseContext") -> list[BaseSprite]:
        """Возвращает все спрайты."""
        sprites: list[BaseSprite] = super().all_sprites
        sprites.extend(
            [
                all_sprites
                for link in self.__links_container or []
                for all_sprites in link.all_sprites
            ],
        )
        return sprites

    @_BaseC4Element.all_tags.getter
    def all_tags(self: "BaseContext") -> list[BaseTag]:
        """Возвращает все теги.

        :return: список тегов
        """
        tags: list[BaseTag] = super().all_tags
        tags.extend(
            [
                tags
                for link in self.__links_container or []
                for tags in link.all_tags
            ],
        )
        return tags

    def __repr__(self: "BaseContext") -> str:
        """Return string representation.

        :raises NotImplementedError: метод не переопределен
        """
        raise NotImplementedError("Метод не переопределен")


class Person(BaseContext):
    """Person."""

    def __init__(
        self: "Person",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать Person."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "Person") -> str:
        """Return string representation."""
        return f"Person{self._repr_inside_pths}"


class PersonExt(BaseContext):
    """PersonExt."""

    def __init__(
        self: "PersonExt",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать PersonExt."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "PersonExt") -> str:
        """Return string representation."""
        return f"Person_Ext{self._repr_inside_pths}"


class System(BaseContext):
    """System."""

    def __init__(
        self: "System",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать System."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "System") -> str:
        """Return string representation."""
        return f"System{self._repr_inside_pths}"


class SystemDb(BaseContext):
    """SystemDb."""

    def __init__(
        self: "SystemDb",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать System."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemDb") -> str:
        """Return string representation."""
        return f"SystemDb{self._repr_inside_pths}"


class SystemQueue(BaseContext):
    """SystemQueue."""

    def __init__(
        self: "SystemQueue",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать System."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemQueue") -> str:
        """Return string representation."""
        return f"SystemQueue{self._repr_inside_pths}"


class SystemExt(BaseContext):
    """SystemExt."""

    def __init__(
        self: "SystemExt",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать SystemExt."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemExt") -> str:
        """Return string representation."""
        return f"System_Ext{self._repr_inside_pths}"


class SystemDbExt(BaseContext):
    """SystemDbExt."""

    def __init__(
        self: "SystemDbExt",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать SystemDbExt."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemDbExt") -> str:
        """Return string representation."""
        return f"SystemDb_Ext{self._repr_inside_pths}"


class SystemQueueExt(BaseContext):
    """SystemQueueExt."""

    def __init__(
        self: "SystemQueueExt",
        label: str,
        descr: str = "",
        sprite: BaseSprite | None = None,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать SystemQueueExt."""
        super().__init__(
            label=label,
            descr=descr,
            sprite=sprite,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemQueueExt") -> str:
        """Return string representation."""
        return f"SystemQueue_Ext{self._repr_inside_pths}"


class Boundary(BaseContext):
    """System."""

    __boundary_type: str

    def __init__(
        self: "Boundary",
        label: str,
        boundary_type: str = "",
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать System."""
        super().__init__(
            label=label,
            descr=None,
            sprite=None,
            link=link,
            tags=tags,
            boundary_type=boundary_type,
            links_container=links_container,
        )
        self.__boundary_type = boundary_type

    def __repr__(self: "Boundary") -> str:
        """Return string representation."""
        return f"Boundary{self._repr_inside_pths}"


class EnterpriseBoundary(BaseContext):
    """EnterpriseBoundary."""

    def __init__(
        self: "EnterpriseBoundary",
        label: str,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать EnterpriseBoundary."""
        super().__init__(
            label=label,
            descr=None,
            sprite=None,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "EnterpriseBoundary") -> str:
        """Return string representation."""
        return f"Enterprise_Boundary{self._repr_inside_pths}"


class SystemBoundary(BaseContext):
    """SystemBoundary."""

    def __init__(
        self: "SystemBoundary",
        label: str,
        link: str | None = None,
        tags: tuple[_ElementTag] | None = None,
        links_container: list[_BaseContainer] | None = None,
    ) -> None:
        """Создать SystemBoundary."""
        super().__init__(
            label=label,
            descr=None,
            sprite=None,
            link=link,
            tags=tags,
            boundary_type=None,
            links_container=links_container,
        )

    def __repr__(self: "SystemBoundary") -> str:
        """Return string representation."""
        return f"System_Boundary{self._repr_inside_pths}"
