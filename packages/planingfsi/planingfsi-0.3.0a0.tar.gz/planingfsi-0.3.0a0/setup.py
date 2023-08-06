# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['planingfsi', 'planingfsi.fe', 'planingfsi.potentialflow']

package_data = \
{'': ['*']}

install_requires = \
['click-log>=0.4.0,<0.5.0',
 'click>=8.0,<9.0',
 'matplotlib>=3.0,<4.0',
 'numpy>=1.15,<2.0',
 'scipy>=1.8.0,<2.0.0']

entry_points = \
{'console_scripts': ['planingfsi = planingfsi.cli:cli']}

setup_kwargs = {
    'name': 'planingfsi',
    'version': '0.3.0a0',
    'description': 'Fluid-Structure Interaction for large deformation planing surfaces',
    'long_description': '# PlaningFSI\n\n[![Run Python Tests](https://github.com/mattkram/planingfsi/workflows/Run%20Python%20Tests/badge.svg)](https://github.com/mattkram/planingfsi/actions)\n[![Coverage](https://codecov.io/gh/mattkram/planingfsi/branch/develop/graph/badge.svg)](https://codecov.io/gh/mattkram/planingfsi)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Docs](https://readthedocs.org/projects/planingfsi/badge/?version=latest)](https://planingfsi.readthedocs.io/en/latest/?badge=latest)\n[![Version](https://img.shields.io/pypi/v/planingfsi.svg)](https://pypi.org/project/planingfsi/)\n[![License](https://img.shields.io/pypi/l/planingfsi.svg)](https://pypi.org/project/planingfsi/)\n\nPlaningFSI is a scientific Python program use to calculate the steady-state response of two-dimensional marine structures planing at constant speed on the free surface with consideration for Fluid-Structure Interaction (FSI) and rigid body motion.\nIt was originally written in 2012-2013 to support my Ph.D. research and has recently (2018) been updated and released as open-source.\n\n## Cautionary Note\n\nI am currently working on releasing this package as open source.\nSince this is my first open-source release, the next few releases on PyPI should not be used for production.\nI will release version 1.0.0 and remove this note once I feel that I have sufficiently cleaned up and documented the code.\n\n## Required Python version\n\nThe code is written in Python and was originally written in Python 2.6.5.\nit has since been updated to require Python 3.6+.\n\n## Installation\n\nPlaningFSI can be installed with pip:\n\n```\npip install planingfsi\n```\n\n## Contributing\n\nTo contribute, you should install the code in developer mode.\n\n```\npoetry install --develop=.\n```\n\n## Getting Started\n\nThe main command-line interface is called `planingFSI` and can be called directly, once appropriate input files have been prepared.\nA collection of examples can be found in the `tutorials` directory in the source package.\n',
    'author': 'Matt Kramer',
    'author_email': 'matthew.robert.kramer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mattkram/planingfsi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
