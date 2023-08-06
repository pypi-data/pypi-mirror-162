"""Отношения."""

from .base import BaseC4Element as _BaseC4Element
from .base import BaseRelation as _BaseRelation
from .tag import RelTag as _RelTag


class Rel(_BaseRelation):
    """Relation."""

    def __init__(
        self: "Rel",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает Relation."""
        super().__init__(
            kind="Rel",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelBack(_BaseRelation):
    """RelBack."""

    def __init__(
        self: "RelBack",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает Relation."""
        super().__init__(
            kind="Rel_Back",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelNeighbor(_BaseRelation):
    """Rel_Neighbor."""

    def __init__(
        self: "RelNeighbor",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает Relation."""
        super().__init__(
            kind="Rel_Neighbor",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelR(_BaseRelation):
    """RelR."""

    def __init__(
        self: "RelR",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает RelR."""
        super().__init__(
            kind="Rel_R",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelL(_BaseRelation):
    """RelL."""

    def __init__(
        self: "RelL",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает RelR."""
        super().__init__(
            kind="Rel_L",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelU(_BaseRelation):
    """RelU."""

    def __init__(
        self: "RelU",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает RelU."""
        super().__init__(
            kind="Rel_U",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class RelD(_BaseRelation):
    """RelD."""

    def __init__(
        self: "RelD",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает RelD."""
        super().__init__(
            kind="Rel_D",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class BiRel(_BaseRelation):
    """RelD."""

    def __init__(
        self: "BiRel",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает BiRel."""
        super().__init__(
            kind="BiRel",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class BiRelR(_BaseRelation):
    """BiRelR."""

    def __init__(
        self: "BiRelR",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает BiRelR."""
        super().__init__(
            kind="BiRel_R",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class BiRelL(_BaseRelation):
    """BiRelL."""

    def __init__(
        self: "BiRelL",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает BiRelL."""
        super().__init__(
            kind="BiRel_L",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class BiRelU(_BaseRelation):
    """BiRelU."""

    def __init__(
        self: "BiRelU",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает BiRelU."""
        super().__init__(
            kind="BiRel_U",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )


class BiRelD(_BaseRelation):
    """BiRelD."""

    def __init__(
        self: "BiRelD",
        links: tuple[_BaseC4Element, _BaseC4Element],
        label: str,
        techn: str = "",
        descr: str = "",
        link: str | None = None,
        tags: tuple[_RelTag, ...] | None = None,
    ) -> None:
        """Создает BiRelD."""
        super().__init__(
            kind="BiRel_D",
            links=links,
            label=label,
            techn=techn,
            descr=descr,
            link=link,
            tags=tags,
        )
