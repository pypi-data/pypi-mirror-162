# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['konstantin_docs',
 'konstantin_docs.dia',
 'konstantin_docs.dia.c4',
 'konstantin_docs.dia.c4.sprite_lib',
 'konstantin_docs.dia.c4.sprite_lib.tupadr3_lib',
 'konstantin_docs.dia.mermaid_er',
 'konstantin_docs.dia.mermaid_state',
 'konstantin_docs.service']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'typing_extensions']

setup_kwargs = {
    'name': 'konstantin-docs',
    'version': '0.0.14',
    'description': 'Генерация документации',
    'long_description': '[![PyPI version](https://badge.fury.io/py/konstantin-docs.svg)](https://badge.fury.io/py/konstantin-docs)\n\n# kroki-python\n\nБиблиотека для генерации диаграмм из текстового описания.\n\nДиаграммы описываются объектами python. Далее геренируются изображения с помощью https://kroki.io.\n\n## Как использовать\n\n1. Создать две папки:\n\n   - dia_src - папка с исходным описанием\n   - dia_dist - папка со сгенерированными изображениями\n\n2. В папке dia_src создаются py-файлы. Названия файлов - произвольные. Можно создавать подкаталоги - структура каталогов будет скопирована в целевую папку dia_dist. Примеры создания можно посмотреть в тестовых диаграммах [пакета](https://github.com/Konstantin-Dudersky/konstantin_docs/tree/main/test).\n\n3. Для генерации можно создать задачу poetepoet. Прописать в файле pyproject.toml:\n\n   ```toml\n   [tool.poetry.dependencies]\n   konstantin_docs = "*"\n   poethepoet = "*"\n   \n   [tool.poe.tasks]\n   docs = {script = "konstantin_docs.main:generate_images(\'dia_src\', \'dia_dist\')"}\n   ```\n\n4. Запустить командой:\n\n    ```sh\n    poetry run poe docs\n    ```\n\n5. Дополнительно можно создать задачу в vscode. Для этого в файле .vscode/tasks.json:\n\n   ```json\n   {\n     "version": "2.0.0",\n     "tasks": [\n       {\n         "label": "docs",\n         "type": "shell",\n         "command": "poetry run poe docs"\n       }\n     ]\n   }\n   ```\n\n   Запускать командой F1 -> Task: Run task -> docs\n\n',
    'author': 'Konstantin-Dudersky',
    'author_email': 'Konstantin.Dudersky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Konstantin-Dudersky/konstantin_docs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
