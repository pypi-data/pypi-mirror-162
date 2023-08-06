"""Точка входа для генерации схем."""

import logging
import os
import os.path
import shutil
from importlib import import_module
from types import ModuleType

from konstantin_docs.dia.base import BaseDiagram


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class ModuleInfo:
    """Модуль для импорта."""

    __imported_module: ModuleType | None = None

    def __init__(
        self: "ModuleInfo",
        path_module: str,
        filename: str,
        path_src: str,
        path_dist: str,
    ) -> None:
        """Create ModuleInfo."""
        self.__path_module = path_module
        self.__filename = filename
        self.__path_src = path_src
        self.__path_dist = path_dist

    @property
    def imported(self: "ModuleInfo") -> ModuleType | None:
        """Возвращает импортированный модуль."""
        return self.__imported_module

    @property
    def path_module(self: "ModuleInfo") -> str:
        """Возвращает путь до исходной папки с модулем."""
        return self.__path_module

    @property
    def path_image(self: "ModuleInfo") -> str:
        """Возвращает путь до целевой папки с изображениями."""
        return self.__path_module.replace(self.__path_src, self.__path_dist)

    def try_import(self: "ModuleInfo") -> None:
        """Попытка импортировать модуль."""
        prefix = self.__path_to_import_prefix()
        if prefix == "":
            module_name = self.__filename
        else:
            module_name = prefix + "." + self.__filename
        logger.info("Попытка импорта %s", module_name)
        self.__imported_module = import_module(module_name)

    def __path_to_import_prefix(self: "ModuleInfo") -> str:
        """Путь до модуля в префикс для импорта модуля."""
        return self.__path_module.replace("/", ".")


def __scan_folder_for_modules(
    path_src: str,
    path_dist: str,
) -> list[ModuleInfo]:
    """Сканируем файлы в папке и создаем список потенциальных модулей."""
    logger.debug("Начинаем сканировать папку и искать модули")
    modules: list[ModuleInfo] = []
    for dirpath, _, filenames in os.walk(path_src):
        logger.debug("Сканирование папки, dirpath: %s", dirpath)
        for module in filenames:
            if module[-3:] != ".py":
                continue
            if module == "main.py":
                continue
            logger.debug("Найден модуль %s", module)
            modules.append(
                ModuleInfo(
                    path_module=dirpath,
                    filename=module[:-3],
                    path_src=path_src,
                    path_dist=path_dist,
                ),
            )
    return modules


def __dia_from_module(module: ModuleType) -> tuple[BaseDiagram]:
    """Список диаграмм из модуля."""
    dias: list[BaseDiagram] = []
    for item in module.__dict__.values():
        if isinstance(item, BaseDiagram):
            dias.append(item)
    return tuple(dias)


def __ignore_files(directory: str, files: list[str]) -> list[str]:
    """Игнорировать файлы при копировании дерева папок."""
    return [f for f in files if os.path.isfile(os.path.join(directory, f))]


def generate_images(path_src: str, path_dist: str) -> None:
    """Основная функция для генерации изображений.

    :param path_src: путь к папке с текстовым описанием диаграмм
    :param path_dist: путь к папке, куда будут сохраняться изображения
    """
    # удаляем целевую папку
    shutil.rmtree(path=path_dist, ignore_errors=True)
    # копируем структуру папок
    shutil.copytree(
        src=path_src,
        dst=path_dist,
        ignore=__ignore_files,
    )
    with open(
        f"{path_dist}/__this_folder_is_automatically_generated__",
        "w",
    ) as f:
        f.write("")
    # сканируем файлы в исходной папке и находим потенциальные модули
    imports = __scan_folder_for_modules(path_src, path_dist)
    # попытка импортировать модули
    imported: list[ModuleInfo] = []
    for mod in imports:
        try:
            mod.try_import()
            logger.debug("Успешно импортирован модуль: %s", mod.imported)
            imported.append(mod)
        except ImportError:
            continue
    # генерируем диаграммы
    for mod, _path in [(mod.imported, mod.path_image) for mod in imported]:
        if mod is None:
            continue
        dias_in_module = __dia_from_module(mod)
        logger.debug(
            "В модуле %s найдено диаграмм: %s",
            mod,
            len(dias_in_module),
        )
        for dia in dias_in_module:
            for dia_format in dia.get_images():
                with open(_path + "/" + dia_format.filename, "wb") as stream:
                    stream.write(dia_format.content)
