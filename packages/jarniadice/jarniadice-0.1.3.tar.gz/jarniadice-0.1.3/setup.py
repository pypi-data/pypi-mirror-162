# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jarniadice']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0']

setup_kwargs = {
    'name': 'jarniadice',
    'version': '0.1.3',
    'description': 'A library for parsing and evaluating Jarnia Dice Notation',
    'long_description': "===========\nJarnia Dice\n===========\nA library for parsing and evaluating Jarnia Dice Notation.\n\nIn the future, we aim to have all the features of standard Dice Notation,\nbut also more.\n\nThe current stage of development is pre-alpha, and I'm running\nthis library only on a private telegram bot and implementing\nthe features as I need.\n\nDocumentation (Draft)\n=====================\nRun three d6 and return the **sum**::\n\n    $ python -m jarniadice '3d6'\n\nRun two d10 and return the value of the **higher**::\n\n    $ python -m jarniadice '2d10kh'\n\nRun two d10 and return the value of the **lower**::\n\n    $ python -m jarniadice '2d10kl'\n\nRun two d10 and return **all** the values as a \n`numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray>`_::\n\n   $ python -m jarniadice '2d10kl'",
    'author': 'Jader Brasil',
    'author_email': 'jaderbrasil@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jaderebrasil/python-roller',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
