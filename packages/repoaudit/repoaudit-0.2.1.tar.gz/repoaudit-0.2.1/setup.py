# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repoaudit']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'python-debian>=0.1.44,<0.2.0',
 'python-gnupg>=0.4.9,<0.5.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['repoaudit = repoaudit:main']}

setup_kwargs = {
    'name': 'repoaudit',
    'version': '0.2.1',
    'description': 'CLI to validate yum/apt repositories',
    'long_description': '# repoaudit\n\nA tool for validating apt and yum repositories.\n\n## Installation and Usage\n\nTo install repoaudit from PyPI:\n\n```\npip install repoaudit\n```\n\nThen run:\n\n```\nrepoaudit --help\n```\n\n## Examples\n\n```\n# validate all distros of azure-cli apt repo\nrepoaudit apt https://packages.microsoft.com/repos/azure-cli/\n\n# validate only focal and bionic distros of azure-cli apt repo\nrepoaudit apt --dists focal,bionic https://packages.microsoft.com/repos/azure-cli/\n\n# validate azurecore repo\nrepoaudit yum https://packages.microsoft.com/yumrepos/azurecore/\n\n# validate all nested yumrepos\nrepoaudit yum -r https://packages.microsoft.com/yumrepos/\n\n# validate all nested aptrepos\nrepoaudit yum -r https://packages.microsoft.com/repos/\n\n# output json results to a file\nrepoaudit yum -r https://packages.microsoft.com/yumrepos/ -o example_file.json\n\n# check metadata signatures by providing public keys\nrepoaudit apt https://packages.microsoft.com/repos/cbl-d -p https://packages.microsoft.com/keys/microsoft.asc,https://packages.microsoft.com/keys/msopentech.asc\n```\n\n## Development\n\n### Setup\n\nFirst install poetry per the [installation docs](https://python-poetry.org/docs/#installation).\n\nThen clone the repo, cd into the repoaudit directory, and run `poetry install`.\n\n### Usage\n\nTo load the poetry shell and run repoaudit:\n\n```\npoetry shell\nrepoaudit\n```\n\nAlternatively you can run:\n\n```\npoetry run repoaudit\n```\n\n## Releasing\n\nFirst bump the version in pyproject.toml. Then commit it:\n\n```\ngit commit -am "0.2.0 Release"\n```\n\nOpen a PR and get it merged. Then go to\n[the Github new release page](https://github.com/microsoft/linux-package-repositories/releases/new)\nand create a new release \n\nOnce that\'s done, pull the tag and use poetry to build it:\n\n```\ngit pull --tags\ngit checkout 0.2.0\npoetry publish --build\n```\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
