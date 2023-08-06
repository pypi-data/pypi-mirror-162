# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_rest_api']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'pytest-rest-api',
    'version': '0.1.0',
    'description': '',
    'long_description': "# Pytest Rest Api\n\nPyTest расширение для тестирования API веб приложений.\n\nВерсия 0.0.1 служит бронью имени на pypi.org\n\n<!-- ## Quick start\n\nПодключение расширения:\n\n```python\n# conftest.py\npytest_plugins = [\n    ...\n    'pytest_rest_api'\n    ...\n]\n```\n\nНастройка подключения:\n\n```python\n# conftest.py\n# TODO: После формирования интерфейса\n```\n\nНаписание тестов:\n\n```python\n# conftest.py\n# TODO: После формирования интерфейса\n```\n\n## Функциональность\n\n### Кастомный клиент запросов к серверу\n\n```python\n# test_request.py\n\ndef test_request(client):\n    # TODO: После формирования интерфейса\n\n### Измерение времени запросов к серверу\n\nКлиент для запросов сохраняет время выполнения запросов к серверу. -->\n",
    'author': 'rocshers',
    'author_email': 'prog.rocshers@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
