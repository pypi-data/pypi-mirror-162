[![PyPI version](https://badge.fury.io/py/konstantin-docs.svg)](https://badge.fury.io/py/konstantin-docs)

# kroki-python

Библиотека для генерации диаграмм из текстового описания.

Диаграммы описываются объектами python. Далее геренируются изображения с помощью https://kroki.io.

## Как использовать

1. Создать две папки:

   - dia_src - папка с исходным описанием
   - dia_dist - папка со сгенерированными изображениями

2. В папке dia_src создаются py-файлы. Названия файлов - произвольные. Можно создавать подкаталоги - структура каталогов будет скопирована в целевую папку dia_dist. Примеры создания можно посмотреть в тестовых диаграммах [пакета](https://github.com/Konstantin-Dudersky/konstantin_docs/tree/main/test).

3. Для генерации можно создать задачу poetepoet. Прописать в файле pyproject.toml:

   ```toml
   [tool.poetry.dependencies]
   konstantin_docs = "*"
   poethepoet = "*"
   
   [tool.poe.tasks]
   docs = {script = "konstantin_docs.main:generate_images('dia_src', 'dia_dist')"}
   ```

4. Запустить командой:

    ```sh
    poetry run poe docs
    ```

5. Дополнительно можно создать задачу в vscode. Для этого в файле .vscode/tasks.json:

   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "docs",
         "type": "shell",
         "command": "poetry run poe docs"
       }
     ]
   }
   ```

   Запускать командой F1 -> Task: Run task -> docs

