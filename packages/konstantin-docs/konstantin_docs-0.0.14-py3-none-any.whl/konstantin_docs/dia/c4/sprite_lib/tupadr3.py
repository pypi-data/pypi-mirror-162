"""tupadr3 lib."""

from konstantin_docs.dia.c4.base import BaseSprite as _BaseSprite
from konstantin_docs.dia.c4.base import BaseSprites as _BaseSprites

from .tupadr3_lib.devicons import DeviconsLib
from .tupadr3_lib.devicons2 import Devicons2Lib
from .tupadr3_lib.font_awesome_5 import FontAwesome5Lib


class _Sprite(_BaseSprite):
    """Tupadr3 library.

    https://github.com/tupadr3/plantuml-icon-font-sprites
    """

    def __init__(
        self: "_Sprite",
        common_sprite: str,
        sprite: _BaseSprites,
    ) -> None:
        """Create sprite tupadr3."""
        super().__init__("tupadr3/common", common_sprite, sprite)


class Devicons(_Sprite):
    """Font Awedome 5."""

    def __init__(self: "Devicons", sprite: DeviconsLib) -> None:
        """Create sprite tupadr3."""
        super().__init__("tupadr3/devicons", sprite)


class Devicons2(_Sprite):
    """Font Awedome 5."""

    def __init__(self: "Devicons2", sprite: Devicons2Lib) -> None:
        """Create sprite tupadr3."""
        super().__init__("tupadr3/devicons2", sprite)


class FontAwesome5(_Sprite):
    """Font Awedome 5."""

    def __init__(self: "_Sprite", sprite: FontAwesome5Lib) -> None:
        """Create sprite tupadr3."""
        super().__init__("tupadr3/font-awesome-5", sprite)
