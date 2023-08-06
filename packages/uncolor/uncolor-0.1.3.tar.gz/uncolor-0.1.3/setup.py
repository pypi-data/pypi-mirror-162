# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uncolor']

package_data = \
{'': ['*']}

install_requires = \
['pytest-datadir>=1.3.1,<2.0.0']

entry_points = \
{'console_scripts': ['uncolor = uncolor:uncolor']}

setup_kwargs = {
    'name': 'uncolor',
    'version': '0.1.3',
    'description': 'strips ANSI colors from a data stream',
    'long_description': "uncolor\n======================\n|LANGUAGE| |VERSION| |LICENSE| |MAINTAINED| |CIRCLECI| |STYLE|\n\n.. |CIRCLECI| image:: https://img.shields.io/circleci/build/gh/rpdelaney/uncolor\n   :target: https://circleci.com/gh/rpdelaney/uncolor/tree/master\n.. |LICENSE| image:: https://img.shields.io/badge/license-Apache%202.0-informational\n   :target: https://www.apache.org/licenses/LICENSE-2.0.txt\n.. |MAINTAINED| image:: https://img.shields.io/maintenance/yes/2022?logoColor=informational\n.. |VERSION| image:: https://img.shields.io/pypi/v/uncolor\n   :target: https://pypi.org/project/uncolor\n.. |STYLE| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n.. |LANGUAGE| image:: https://img.shields.io/pypi/pyversions/uncolor\n\nStrips ANSI color sequences from the stream on standard input, printing the result on the standard output.\n\nThat's it.\n",
    'author': 'Ryan Delaney',
    'author_email': 'ryan.patrick.delaney+git@protonmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://pypi.org/project/uncolor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
