# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plenary']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'plenary',
    'version': '1.3.3',
    'description': 'A library of convenient utility methods and classes',
    'long_description': "# plenary\n\n![license](https://img.shields.io/github/license/swinburne-sensing/plenary) ![python version](https://img.shields.io/pypi/pyversions/plenary) ![testing](https://github.com/swinburne-sensing/plenary/actions/workflows/python.yml/badge.svg) ![issues](https://img.shields.io/github/issues/swinburne-sensing/plenary)\n\n\nA library of convenient utility methods and classes. Designed to work in pure python.\n\n## Acknowledgments\n\nDeveloped at [Swinburne University of Technology](https://swin.edu.au). If used in an academic project, please consider citing this work as it helps attract funding and track research outputs:\n\n```\nC. J. Harrison and M. Shafiei. plenary. (2022). [Online]. doi: http://dx.doi.org/xxxxx\n```\n\n*This activity received funding from [ARENA](https://arena.gov.au) as part of ARENA’s Research and Development Program – Renewable Hydrogen for Export (Contract No. 2018/RND012). The views expressed herein are not necessarily the views of the Australian Government, and the Australian Government does not accept responsibility for any information or advice contained herein.*\n\n*The work has been supported by the [Future Energy Exports CRC](https://www.fenex.org.au) whose activities are funded by the Australian Government's Cooperative Research Centre Program.*\n",
    'author': 'Chris Harrison',
    'author_email': '629204+ravngr@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/swinburne-sensing/plenary',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
