# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ruscorpora']

package_data = \
{'': ['*']}

install_requires = \
['rnc>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'ruscorpora',
    'version': '0.10.0',
    'description': 'Links to https://github.com/kunansy/rnc',
    'long_description': '# Ruscorpora\n\nThe project links to Russian National Corpus [library](https://github.com/kunansy/rnc).\n',
    'author': 'kunansy',
    'author_email': 'kolobov.kirill@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://kunansy.github.io/RNC/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
