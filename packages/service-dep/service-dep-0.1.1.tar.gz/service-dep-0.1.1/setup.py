# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['service',
 'service.ext',
 'service.logging',
 'service.types',
 'tests',
 'tests.ext',
 'tests.fn',
 'tests.i18n']

package_data = \
{'': ['*']}

modules = \
['README', '.gitignore', 'pyproject']
install_requires = \
['Faker>=13.15.1,<14.0.0',
 'PyYAML>=6.0,<7.0',
 'Pygments>=2.12.0,<3.0.0',
 'asgi-lifespan>=1.0.1,<2.0.0',
 'fastapi>=0.79.0,<0.80.0',
 'fire>=0.4.0,<0.5.0',
 'httpx-auth>=0.15.0,<0.16.0',
 'jsonrpcserver>=5.0.7,<6.0.0',
 'logging-json>=0.2.1,<0.3.0',
 'pytest-asyncio==0.18.3',
 'pytest-httpx==0.21.0',
 'pytest-logger>=0.5.1,<0.6.0',
 'pytest-mock>=3.8.2,<4.0.0',
 'pytest>=7.1.2,<8.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-i18n>=0.3.9,<0.4.0',
 'sentry-sdk>=1.9.2,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'uvicorn>=0.17.6,<0.18.0',
 'yarl>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'service-dep',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'everhide',
    'author_email': 'i.tolkachnikov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
