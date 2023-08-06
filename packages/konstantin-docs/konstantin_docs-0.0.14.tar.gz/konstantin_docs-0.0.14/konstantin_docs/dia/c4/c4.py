"""Модель C4.

Описание - https://c4model.com/
Реализация на PlantUML - https://github.com/plantuml-stdlib/C4-PlantUML
"""

import logging

from konstantin_docs.dia.base import BaseDiagram as _BaseDiagram
from konstantin_docs.dia.base import Image
from konstantin_docs.service import kroki as _kroki

from . import component, container, context, rel, sprite, tag
from .base import BaseRelation as _BaseRelation
from .base import BaseSprite as _BaseSprite
from .base import BaseTag as _BaseTag

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


# Diagram ---------------------------------------------------------------------

TEMPLATE_DIAGRAM: str = """@startuml

!include C4_Dynamic.puml
{sprites}
{title}
{tag}
{context}
{container}
{rels}
SHOW_LEGEND()
@enduml
"""


class C4(_BaseDiagram):
    """Диаграмма C4."""

    __title: str
    __links_context: list[context.BaseContext] | None
    __links_container: list[container.BaseContainer] | None
    __links_component: list[component.BaseComponent] | None
    __link_rels: list[_BaseRelation] | None

    def __init__(
        self: "C4",
        filename: str,
        title: str = "Diagram title",
        links_context: list[context.BaseContext] | None = None,
        links_container: list[container.BaseContainer] | None = None,
        links_component: list[component.BaseComponent] | None = None,
        links_rel: list[_BaseRelation] | None = None,
    ) -> None:
        """Создает объект диаграммы.

        :param filename: имя файла, без расширения
        :param title: заголовок диаграммы
        """
        super().__init__(filename)
        self.__title = title
        self.__links_context = links_context
        self.__links_container = links_container
        self.__links_component = links_component
        self.__link_rels = links_rel

    @property
    def _format_sprites(self: "C4") -> str:
        """Возвращает все спрайты.

        :return: форматированные спрайты
        """
        all_sprites: list[_BaseSprite] = []
        all_sprites.extend(
            [
                all_sprites
                for link in self.__links_context or []
                for all_sprites in link.all_sprites
            ],
        )
        all_sprites.extend(
            [
                all_sprites
                for link in self.__links_container or []
                for all_sprites in link.all_sprites
            ],
        )
        all_sprites.extend(
            [
                all_sprites
                for link in self.__links_component or []
                for all_sprites in link.all_sprites
            ],
        )
        common: set[str] = set()
        sprites: set[str] = set()
        for spr in all_sprites:
            common.add(spr.common)
            sprites.add(spr.sprite_full)
        out: str = ""
        if len(common) > 0:
            out += "\n".join(common) + "\n" + "\n".join(sprites)
        return out

    @property
    def _format_tags(self: "C4") -> str:
        """Возвращает объявление для всех тегов.

        :return:  форматированные теги
        """
        all_tags: list[_BaseTag] = []
        all_tags.extend(
            [
                all_tags
                for link in self.__links_context or []
                for all_tags in link.all_tags
            ],
        )
        all_tags.extend(
            [
                all_tags
                for link in self.__links_container or []
                for all_tags in link.all_tags
            ],
        )
        all_tags.extend(
            [
                all_tags
                for link in self.__links_component or []
                for all_tags in link.all_tags
            ],
        )
        repr_tags: set[str] = set([t.repr_declaration() for t in all_tags])
        out: str = ""
        if len(repr_tags) > 0:
            out += "\n".join(repr_tags)
        return out

    def get_images(self: "C4") -> tuple[Image]:
        """Возвращает кортеж файлов.

        :return: кортеж файлов
        """
        images: list[Image] = []
        text: str = repr(self)
        images.append(self._get_text_file(".puml"))
        try:
            for fmt in (_kroki.OutputFormats.PNG, _kroki.OutputFormats.SVG):
                images.append(
                    Image(
                        filename=self.filename + "." + fmt.value,
                        content=_kroki.get_image(
                            source=text,
                            diagram_type=_kroki.DiagramTypes.C4PLANTUML,
                            output_format=fmt,
                        ),
                    ),
                )
        except RuntimeError as exc:
            logger.exception(exc)
        return tuple(images)

    def __repr__(self: "C4") -> str:
        """Return string representation.

        :return: string representation
        """
        return TEMPLATE_DIAGRAM.format(
            tag=self._format_tags,
            sprites=self._format_sprites,
            title=f"title {self.__title}" if self.__title != "" else "",
            context="".join(
                [repr(context) for context in (self.__links_context or [])],
            ),
            container="".join(
                [
                    repr(container)
                    for container in (self.__links_container or [])
                ],
            ),
            rels="".join([repr(r) for r in (self.__link_rels or [])]),
        )


if __name__ == "__main__":
    _ = sprite.tupadr3.FontAwesome5(sprite.tupadr3.FontAwesome5Lib.AD)
    _ = tag.ElementTag(
        tag_stereo="123",
    )
    _ = rel.Rel(label="", links=(context.System("1"), context.System("2")))
