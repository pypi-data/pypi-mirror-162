# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['refurb',
 'refurb.checks',
 'refurb.checks.builtin',
 'refurb.checks.pathlib',
 'refurb.checks.string']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.971,<0.972']

entry_points = \
{'console_scripts': ['refurb = refurb.__main__:main']}

setup_kwargs = {
    'name': 'refurb',
    'version': '0.2.0',
    'description': 'A tool for refurbish and modernize Python codebases',
    'long_description': None,
    'author': 'dosisod',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
