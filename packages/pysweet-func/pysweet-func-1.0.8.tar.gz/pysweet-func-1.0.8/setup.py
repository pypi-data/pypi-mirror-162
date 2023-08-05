# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysweet']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pysweet-func',
    'version': '1.0.8',
    'description': 'Composable Python for production via syntactic sugar',
    'long_description': "pysweet-func\n============\n\n|test| |codecov| |Documentation Status| |PyPI version|\n\nWhy ``pysweet``?\n----------------\n\nPython can sometimes be unwieldy in production.\n\nConsider the following 3 variants\nof the same logic:\n\n.. code:: python\n\n   acc = []\n\n   for x in range(10):\n       y = x + 1\n\n       if y % 2 == 0:\n           acc.extend([y, y * 2])\n\n.. code:: python\n\n   acc = [\n       z for y in (x + 1 for x in range(10))\n       for z in [y, y * 2] if y % 2 == 0\n   ]\n\n.. code:: python\n\n   from itertools import chain\n\n   acc = list(chain.from_iterable(map(\n       lambda x: [x, x * 2],\n       filter(\n           lambda x: x % 2 == 0,\n           map(lambda x: x + 1, range(10)),\n       ),\n   )))\n\n* The first is in the imperative style;\n  it can become convoluted as requirements evolve.\n\n* The second uses comprehensions,\n  which can get complicated when nested.\n\n* The last utilizes functional programming:\n  more modular, but not as readable.\n\nIn JavaScript, the same logic is simpler:\n\n.. code:: js\n\n   acc = [...Array(10).keys()]\n       .map(x => x + 1)\n       .filter(x => x % 2 === 0)\n       .flatMap(x => [x, x * 2])\n\nCan we write analogous code in Python?\n\nNow you can with ``pysweet``:\n\n.. code:: python\n\n   from pysweet import Iterable_\n\n   acc = (\n       Iterable_(range(10))\n       .map(lambda x: x + 1)\n       .filter(lambda x: x % 2 == 0)\n       .flat_map(lambda x: [x, x * 2])\n       .to_list()\n   )\n\nCompared to many excellent alternatives,\n``pysweet`` is lightweight\nwith fewer than 100 lines of code.\n\nBeing only syntactic sugar, ``pysweet``:\n\n* has little performance overhead;\n* does not complicate debugging;\n* makes onboarding new developers easy.\n\n``pysweet`` has successfully been used in production.\n\nSweeten Python with ``pysweet``!\n\nFeatures\n--------\n\nFluent iterable\n~~~~~~~~~~~~~~~\n\nIterable with method chaining\nin the style of JavaScript and Scala.\n\n.. code:: python\n\n   from pysweet import Iterable_\n\n   (\n       Iterable_([1, 2])\n       .map(lambda x: x + 1)\n       .to_list()\n   )\n   # [2, 3]\n\nMulti-expression lambda\n~~~~~~~~~~~~~~~~~~~~~~~\n\nAs in many modern languages,\neven a systems one like Go.\n\n.. code:: python\n\n   from pysweet import block_\n\n   val = lambda: block_(\n       x := 1,\n       x + 1,\n   )\n   # val() == 2\n\nStatements as expressions\n~~~~~~~~~~~~~~~~~~~~~~~~~\n\nComposable control flow as in functional languages\nsuch as Scala and Haskell.\n\nBonus: ``if_`` is the ternary operator\nin the natural order.\n\n.. code:: python\n\n   from pysweet import if_, try_, raise_\n\n   if_(\n       True,\n       lambda: 1,\n       lambda: 2,\n   )\n   # 1\n\n   try_(\n       lambda: raise_(Exception('test')),\n       catch=lambda e: str(e),\n   )\n   # 'test'\n\nDocumentation\n-------------\n\n-  `Read the Docs <https://pysweet-func.readthedocs.io>`__\n\nInstallation\n------------\n\n-  `PyPI <https://pypi.org/project/pysweet-func>`__\n\n.. |test| image:: https://github.com/natso26/pysweet-func/actions/workflows/test.yml/badge.svg?branch=main&event=push\n.. |codecov| image:: https://codecov.io/gh/natso26/pysweet-func/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/natso26/pysweet-func\n.. |Documentation Status| image:: https://readthedocs.org/projects/pysweet-func/badge/?version=latest\n   :target: https://pysweet-func.readthedocs.io/en/latest/?badge=latest\n.. |PyPI version| image:: https://badge.fury.io/py/pysweet-func.svg\n   :target: https://badge.fury.io/py/pysweet-func\n",
    'author': 'Nat Sothanaphan',
    'author_email': 'natsothanaphan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/natso26/pysweet-func',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
