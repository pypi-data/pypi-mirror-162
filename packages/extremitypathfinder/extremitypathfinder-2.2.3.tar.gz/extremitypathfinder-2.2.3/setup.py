# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extremitypathfinder']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22,<2.0']

entry_points = \
{'console_scripts': ['extremitypathfinder = '
                     'extremitypathfinder.command_line:main']}

setup_kwargs = {
    'name': 'extremitypathfinder',
    'version': '2.2.3',
    'description': 'python package implementing a multivariate Horner scheme for efficiently evaluating multivariate polynomials',
    'long_description': '===================\nextremitypathfinder\n===================\n\n\n.. image:: https://api.travis-ci.org/jannikmi/extremitypathfinder.svg?branch=master\n    :target: https://travis-ci.org/jannikmi/extremitypathfinder\n\n.. image:: https://readthedocs.org/projects/extremitypathfinder/badge/?version=latest\n    :alt: documentation status\n    :target: https://extremitypathfinder.readthedocs.io/en/latest/?badge=latest\n\n.. image:: https://img.shields.io/pypi/wheel/extremitypathfinder.svg\n    :target: https://pypi.python.org/pypi/extremitypathfinder\n\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n\n.. image:: https://pepy.tech/badge/extremitypathfinder\n    :alt: Total PyPI downloads\n    :target: https://pepy.tech/project/extremitypathfinder\n\n.. image:: https://img.shields.io/pypi/v/extremitypathfinder.svg\n    :alt: latest version on PyPI\n    :target: https://pypi.python.org/pypi/extremitypathfinder\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\npython package for fast geometric shortest path computation in 2D multi-polygon or grid environments based on visibility graphs.\n\n\n.. image:: ./docs/_static/title_demo_plot.png\n\n\nQuick Guide:\n\n.. code-block:: console\n\n    pip install extremitypathfinder\n\n\n.. code-block:: python\n\n    from extremitypathfinder import PolygonEnvironment\n\n    environment = PolygonEnvironment()\n    # counter clockwise vertex numbering!\n    boundary_coordinates = [(0.0, 0.0), (10.0, 0.0), (9.0, 5.0), (10.0, 10.0), (0.0, 10.0)]\n    # clockwise numbering!\n    list_of_holes = [\n        [\n            (3.0, 7.0),\n            (5.0, 9.0),\n            (4.5, 7.0),\n            (5.0, 4.0),\n        ],\n    ]\n    environment.store(boundary_coordinates, list_of_holes, validate=False)\n    environment.prepare()\n    start_coordinates = (4.5, 1.0)\n    goal_coordinates = (4.0, 8.5)\n    path, length = environment.find_shortest_path(start_coordinates, goal_coordinates)\n\n\nFor more refer to the `documentation <https://extremitypathfinder.readthedocs.io/en/latest/>`__.\n\n\nAlso see:\n`GitHub <https://github.com/jannikmi/extremitypathfinder>`__,\n`PyPI <https://pypi.python.org/pypi/extremitypathfinder/>`__\n',
    'author': 'jannikmi',
    'author_email': 'github@michelfe.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://extremitypathfinder.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
