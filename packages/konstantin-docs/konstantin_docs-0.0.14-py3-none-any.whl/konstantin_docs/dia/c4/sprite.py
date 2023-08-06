r"""Sprite.

Для генерации перечислений на основе списка файлов:
- в папке с файлами создать файл _generate.py:
-------------------------------------------------------------------------------
import os

OUT_FILENAME = "_enum.txt"
SCRIPT_FILENAME = "_generate.py"

sprites: set[str] = set()
for _, _, filenames in os.walk(os.getcwd()):
    # filenames: list[str] = filenames
    for filename in filenames:
        if filename in [OUT_FILENAME, SCRIPT_FILENAME]:
            continue
        sprite_parts = filename.split(".")[:-1]
        sprites.add(".".join(sprite_parts))

with open(OUT_FILENAME, "w", encoding="utf-8") as stream:
    for sprite in sorted(sprites):
        line = f'    {sprite.upper()} = "{sprite}"\n'
        stream.write(line)

-------------------------------------------------------------------------------
- настроить переменные BASE и PATH
- запустить командой python3 _generate.py
- содержимое файла _enum.txt вставить в перечиление
"""
from .sprite_lib import tupadr3

if __name__ == "__main__":
    _ = tupadr3.FontAwesome5(tupadr3.FontAwesome5Lib.AD)
