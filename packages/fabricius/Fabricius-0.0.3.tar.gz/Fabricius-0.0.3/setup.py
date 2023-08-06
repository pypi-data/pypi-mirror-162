# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fabricius', 'fabricius.contracts']

package_data = \
{'': ['*']}

install_requires = \
['chevron>=0.14.0,<0.15.0',
 'inflection>=0.5.1,<0.6.0',
 'rich>=12.4.4,<13.0.0',
 'typing-extensions>=4.2.0,<5.0.0']

extras_require = \
{'docs': ['Sphinx>=5.0.2,<6.0.0',
          'furo>=2022.6.21,<2023.0.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0']}

setup_kwargs = {
    'name': 'fabricius',
    'version': '0.0.3',
    'description': 'Fabricius: The supportive templating engine for Python!',
    'long_description': "# Fabricius\n\nFabricius - A Python 3.10 Project Template engine with superpowers!\n\n> :warning: Fabricius is a work in progress! Please, play with it with a grain of salt; expect bugs, crashes, non-documented portion of the application & more unexpected behavior.\n\nDocumentation: <https://fabricius.readthedocs.io>\n\n> :warning: Fabricius still does not comes with it's CLI tool! It is a work in progress!\n",
    'author': 'Predeactor',
    'author_email': 'pro.julien.mauroy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Predeactor/Fabricius',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
