"""Interaction with https://kroki.io."""

import base64
import json
import zlib
from enum import Enum

import requests

URL = "https://kroki.io"


class DiagramTypes(Enum):
    """Diagram types."""

    GRAPHIZ = "graphiz"
    NWDIAG = "nwdiag"
    C4PLANTUML = "c4plantuml"
    MERMAID = "mermaid"


class OutputFormats(Enum):
    """Output formats."""

    PNG = "png"
    SVG = "svg"


def get_image(
    source: str,
    diagram_type: DiagramTypes,
    output_format: OutputFormats,
) -> bytes:
    """Возвращает изображение.

    :raises RuntimeError: отрицательный ответ от сервера
    :param source: текст диаграммы
    :param diagram_type: тип диаграммы
    :param output_format: формат изображения для генерации
    :return: изображение
    """
    req_type = "post"
    match req_type:
        case "post":
            response = requests.post(
                url=URL,
                data=json.dumps(
                    {
                        "diagram_source": source,
                        "diagram_type": diagram_type.value,
                        "output_format": output_format.value,
                    },
                ),
            )
        case "get":
            compressed = base64.urlsafe_b64encode(
                zlib.compress(source.encode("utf-8"), 9),
            ).decode("ascii")
            response = requests.get(
                url=URL
                + "/"
                + diagram_type.value
                + "/"
                + output_format.value
                + "/"
                + compressed,
            )
    if response.status_code != 200:
        raise RuntimeError(response.content)
    return response.content
