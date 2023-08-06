# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['disquest_utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.40,<2.0.0',
 'asyncpg>=0.26.0,<0.27.0',
 'uvloop>=0.16.0,<0.17.0']

extras_require = \
{'asyncmy': ['asyncmy>=0.2.5,<0.3.0']}

setup_kwargs = {
    'name': 'disquest-utils',
    'version': '1.1.0',
    'description': "A set of async utils for Miku's DisQuest Cog",
    'long_description': '<div align=center>\n\n\n# DisQuest-Utils\n\n![PyPI](https://img.shields.io/pypi/v/disquest-utils?label=PyPi&logo=pypi&logoColor=white) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/disquest-utils?label=Python&logo=python&logoColor=white)\n![PyPI - License](https://img.shields.io/pypi/l/disquest-utils?label=License&logo=github&logoColor=white)\n\nA set of async utils for DisQuest\n\n<div align=left>\n\n# Info\n\nDisQuest is an base system for storing and giving users on Discord xp. This is just the base set of coroutines needed in order to use DisQuest. DisQuest uses PostgreSQL. Alternatively, if you plan on passing in your own URI (which probably u would have to), DisQuest technically also supports MySQL/MariaDB. For MySQL/MariaDB, use `asyncmy` instead of `asyncpg`\n\n# Installing\n\n\nWith Asyncpg (default):\n\n```sh\npip install disquest-utils\n```\nWith Asyncmy:\n\n```sh\npip install disquest-utils[asyncmy]\n```\n\n# URI Connections\n\nDisQuest-Utils accepts URI connections in order to connection to the database. It is recommended to have python-dotenv installed, and then add the credentials as needed. The example below are only for examples, and adjust them as needed\n\nAsyncpg:\n\n```python\nCONNECTION_URI = "postgresql+asyncpg://user:password@host:port/dbname[?key=value&key=value...]"\n```\n\nAsyncmy:\n\n```python\nCONNECTION_URI = "mysql+asyncmy://user:password@host:port/dbname[?key=value&key=value...]"\n```\n\nNow pass the variable `CONNECTION_URI` as the uri arg of any method, and you should be ready to go',
    'author': 'No767',
    'author_email': '73260931+No767@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/No767/DisQuest-Utils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
