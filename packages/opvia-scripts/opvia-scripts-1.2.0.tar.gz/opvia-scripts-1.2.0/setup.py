# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['opvia_scripts', 'opvia_scripts.types']

package_data = \
{'': ['*']}

install_requires = \
['Pyrebase4>=4.5.0,<5.0.0',
 'altair>=4.2.0,<5.0.0',
 'fastapi-camelcase>=1.0.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.27.0,<3.0.0',
 'setuptools==61.2.0']

setup_kwargs = {
    'name': 'opvia-scripts',
    'version': '1.2.0',
    'description': '',
    'long_description': "# Opvia Scripts\n\n[![CI](https://github.com/opvia/opvia-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/opvia/opvia-scripts/actions/workflows/ci.yml)\n[![codecov](https://codecov.io/gh/opvia/opvia-scripts/branch/main/graph/badge.svg?token=NSNITDCIUW)](https://codecov.io/gh/opvia/opvia-scripts)\n\nThis repo is used to build custom cards on the Opvia platform.\n\n## Developing\n\nInstall [Poetry](https://python-poetry.org/) and `poetry install` the project\n\nPRs made to this repo require approval from another developer. There should be reasonable tests for all functionality. Tests should protect backwards-compatibility of all of our changes.\n\nNew changes should be accompanied by appropriate updates to the [docs](docs/), covering:\n- Relevant class and function definitions for custom card writers\n- Simple examples covering installed script functionality\n- Independently readable in-app scripting versions of the same examples\n\n### Useful Commands\n\nNote: if Poetry is managing a virtual environment for you, you may need to use `poetry run poe` instead of `poe`\n\n- `poe autoformat` - Autoformat code\n- `poe lint` - Linting\n- `poe test` - Run Tests\n- `poe docs` - Build docs\n\n### Release\n\nRelease a new version by manually running the release action on GitHub with a 'major', 'minor', or 'patch' version bump selected.\nThis will create an push a new semver tag of the format `v1.2.3`.\n\nPushing this tag will trigger an action to release a new version of your library to PyPI.\n\nOptionally create a release from this new tag to let users know what changed.\n",
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/opvia/opvia-scripts',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
