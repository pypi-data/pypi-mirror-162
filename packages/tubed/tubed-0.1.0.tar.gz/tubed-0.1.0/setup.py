# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tubed']

package_data = \
{'': ['*']}

install_requires = \
['pytube>=12.1.0,<13.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['tubed = tubed.main:app']}

setup_kwargs = {
    'name': 'tubed',
    'version': '0.1.0',
    'description': 'Youtube downloader',
    'long_description': '# Youtube downloader CLI\n\n![build](https://github.com/MousaZeidBaker/tubed/workflows/Publish/badge.svg)\n[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)\n![python_version](https://img.shields.io/badge/python-%3E=3.8-blue)\n[![pypi_v](https://img.shields.io/pypi/v/tubed)](https://pypi.org/project/tubed)\n\n## Usage\n\nShow help message and exit\n```shell\ntubed --help\n```\n\nDownload video from URL\n```shell\ntubed --url https://www.youtube.com/watch?v=xFrGuyw1V8s\n```\n\nDownload only audio\n```shell\ntubed --url https://www.youtube.com/watch?v=xFrGuyw1V8s --only-audio\n```\n\nDownload from URLs specified in the [example.txt](./playlists/example.txt)\nfile\n```shell\ntubed --url-file playlists/example.txt\n```\n\n## Contributing\nContributions are welcome via pull requests.\n\n## Issues\nIf you encounter any problems, please file an\n[issue](https://github.com/MousaZeidBaker/tubed/issues) along with a detailed\ndescription.\n\n## Develop\nActivate virtual environment\n```shell\npoetry shell\n```\n\nInstall dependencies\n```shell\npoetry install --remove-untracked\n```\n\nInstall git hooks\n```shell\npre-commit install --hook-type pre-commit\n```\n\nRun linter\n```shell\nflake8 .\n```\n\nFormat code\n```shell\nblack .\n```\n\nSort imports\n```shell\nisort .\n```\n\nInstall current project from branch\n```shell\npoetry add git+https://github.com/MousaZeidBaker/tubed.git#branch-name\n```\n',
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/tubed',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
