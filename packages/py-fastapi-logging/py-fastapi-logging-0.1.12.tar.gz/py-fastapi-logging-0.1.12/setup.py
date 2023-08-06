# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_fastapi_logging',
 'py_fastapi_logging.config',
 'py_fastapi_logging.formatters',
 'py_fastapi_logging.middlewares',
 'py_fastapi_logging.middlewares.utils',
 'py_fastapi_logging.schemas',
 'py_fastapi_logging.utils']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70', 'orjson>=3.7,<4.0']

extras_require = \
{'aiohttp': ['aiohttp>=3,<4'], 'all': ['aiohttp>=3,<4']}

setup_kwargs = {
    'name': 'py-fastapi-logging',
    'version': '0.1.12',
    'description': 'FastAPI Logging',
    'long_description': '# py-fastapi-logging\n\n## ENV-переменные для управления логами\n#### Уровень логов. debug - для площадок отладки, info - для PROM\nLOG_LEVEL=info\n#### Формат логов: SIMPLE (обычный) или JSON (JSON-STDOUT - лог в формате json в поток stdout)\nLOG_FORMAT=SIMPLE\n#### Папка, в которой будут лежать логи\nLOG_DIR=/var/log/<APP NAME>\n#### Название файла лога\nLOG_FILENAME=production.log\n#### Фильтруемые ключи в payload и request_params\nLOG_EXCLUDE_FIELDS=field1,field2,field3\n#### Добавление переменных в лог (JSON-формат) из переменных окружения\nLOG_ENV_EXTRA="field1:ENV_VAR_NAME_1,field2:ENV_VAR_NAME_2"\n\n\n## Интеграция в FastAPI приложение\n```python\nfrom fastapi import FastAPI\nfrom py_fastapi_logging.middlewares.logging import LoggingMiddleware\napp = FastAPI()\napp.add_middleware(LoggingMiddleware, app_name=\'my_app_name\')\n```\n\n## Использование логгера в приложениях не на FastAPI\n```python\nimport logging\nfrom py_fastapi_logging.config.config import init_logger\ninit_logger(app_name=\'my_app_name\')\nlogger = logging.getLogger()\n```\n\n',
    'author': 'RockITSoft',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
