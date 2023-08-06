# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['strapp',
 'strapp.click',
 'strapp.dramatiq',
 'strapp.flask',
 'strapp.http',
 'strapp.sqlalchemy']

package_data = \
{'': ['*']}

extras_require = \
{':(python_version >= "3.6" and python_version < "3.7") and (extra == "click" or extra == "flask")': ['dataclasses'],
 ':python_version <= "3.10"': ['typing_extensions>=3.10'],
 'click': ['click'],
 'datadog': ['configly', 'datadog'],
 'dramatiq': ['dramatiq[redis]', 'redis>=4.3.4,<5.0.0'],
 'flask': ['flask', 'flask_reverse_proxy'],
 'http': ['setuplog>=0.2.2', 'backoff>=1.11.1,<2.0.0'],
 'sentry': ['sentry-sdk', 'requests'],
 'sqlalchemy': ['sqlalchemy']}

setup_kwargs = {
    'name': 'strapp',
    'version': '0.3.14',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
