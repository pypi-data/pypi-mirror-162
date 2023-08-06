# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wildcatter']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4',
 'gym>=0.21,<0.22',
 'stable-baselines3>=1.6.0,<2.0.0',
 'torch>=1.12.0,<2.0.0']

extras_require = \
{'hello_world': ['pygame==2.1.0', 'pyglet>=1.5.26,<2.0.0']}

entry_points = \
{'console_scripts': ['wildcatter = wildcatter.__main__:main']}

setup_kwargs = {
    'name': 'wildcatter',
    'version': '0.0.4',
    'description': 'Wildcatter',
    'long_description': "# Wildcatter\n\n[![PyPI](https://img.shields.io/pypi/v/wildcatter.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/wildcatter.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/wildcatter)][python version]\n[![License](https://img.shields.io/pypi/l/wildcatter)][license]\n\n[![Read the documentation at https://wildcatter.readthedocs.io/](https://img.shields.io/readthedocs/wildcatter/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/GeoML-SIG/wildcatter/workflows/Tests/badge.svg)][tests]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/wildcatter/\n[status]: https://pypi.org/project/wildcatter/\n[python version]: https://pypi.org/project/wildcatter\n[read the docs]: https://wildcatter.readthedocs.io/\n[tests]: https://github.com/GeoML-SIG/wildcatter/actions?workflow=Tests\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\nReinforcement learning framework for well placement and optimization\n\n## Features\n\n- TODO\n\n## Requirements\n\n- TODO\n\n## Installation\n\nYou can install _Wildcatter_ via [pip] from [PyPI]:\n\n```console\n$ pip install wildcatter\n```\n\n## Usage\n\nPlease see the [Command-line Reference] for details.\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [Apache 2.0 license][license],\n_Wildcatter_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/GeoML-SIG/wildcatter/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/GeoML-SIG/wildcatter/blob/main/LICENSE\n[contributor guide]: https://github.com/GeoML-SIG/wildcatter/blob/main/CONTRIBUTING.md\n[command-line reference]: https://wildcatter.readthedocs.io/en/latest/usage.html\n",
    'author': 'Altay Sansal',
    'author_email': 'tasansal@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/GeoML-SIG/wildcatter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
