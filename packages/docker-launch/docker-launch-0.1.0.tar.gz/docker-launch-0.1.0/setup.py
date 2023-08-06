# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docker_launch']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0', 'paramiko>=2.11.0,<3.0.0', 'tomlkit>=0.11.1,<0.12.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.4,<5.0',
                             'typing-extensions>=4.3,<5.0']}

entry_points = \
{'console_scripts': ['check = docker_launch.ssh:interactively_check_ssh_key']}

setup_kwargs = {
    'name': 'docker-launch',
    'version': '0.1.0',
    'description': 'Create and launch docker images on multiple hosts.',
    'long_description': '# docker-launch\n\n[![PyPI](https://img.shields.io/pypi/v/docker-launch.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/docker-launch/)\n[![Python](https://img.shields.io/pypi/pyversions/docker-launch.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/docker-launch/)\n[![Test](https://img.shields.io/github/workflow/status/necst-telescope/docker-launch/Test?logo=github&label=Test&style=flat-square)](https://github.com/necst-telescope/docker-launch/actions)\n[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](https://github.com/necst-telescope/docker-launch/blob/main/LICENSE)\n\nCreate and launch docker images on multiple hosts.\n\n## Features\n\nThis library provides:\n\n- TBU\n\n## Installation\n\n```shell\npip install docker-launch\n```\n\n## Usage\n\nTBU\n\n---\n\nThis library is using [Semantic Versioning](https://semver.org).\n',
    'author': 'KaoruNishikawa',
    'author_email': 'k.nishikawa@a.phys.nagoya-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/necst-telescope/docker-launch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
