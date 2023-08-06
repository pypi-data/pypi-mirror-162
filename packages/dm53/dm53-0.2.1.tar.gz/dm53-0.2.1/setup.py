# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dm53', 'dm53.models']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.36,<2.0.0', 'pydantic>=1.9.1,<2.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['dm53 = dm53.main:app']}

setup_kwargs = {
    'name': 'dm53',
    'version': '0.2.1',
    'description': 'Domain monitoring & registration with AWS route53',
    'long_description': '# Domain monitoring & registration with AWS route53\n\n![build](https://github.com/MousaZeidBaker/dm53/workflows/Publish/badge.svg)\n[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)\n![python_version](https://img.shields.io/badge/python-%3E=3.8-blue)\n[![pypi_v](https://img.shields.io/pypi/v/dm53)](https://pypi.org/project/dm53)\n\n## Usage\n\nShow help message and exit\n```shell\ndm53 --help\n```\n\nCheck availability of a domain\n```shell\ndm53 check --domain-name example.com\n```\n\n> Note: Make sure AWS credentials are configured, following example uses env\n> variables\n> ```shell\n> AWS_ACCESS_KEY_ID=my-access-key \\\n> AWS_SECRET_ACCESS_KEY=my-secret-access-key \\\n> dm53 check --domain-name example.com\n> ```\n> for more details see [boto3\n> docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)\n\nKeep checking with a 5 seconds interval until the domain becomes available\n```shell\ndm53 check --domain-name example.com --monitor --interval 5\n```\n\nRegister a domain if available\n\n```shell\ndm53 check --domain-name example.com --register --path /path/to/registration-details.json\n```\n\n> Note: Registration details must be provided through a JSON file, see [this\n> example](https://github.com/MousaZeidBaker/dm53/blob/master/example-registration-details.json)\n> or read more in [AWS\n> docs](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_RegisterDomain.html)\n\nRun in background to ignore hangup signal with\n[nohup](https://man7.org/linux/man-pages/man1/nohup.1.html), forward output to\n`examplecom.out`\n```shell\nnohup dm53 check --domain-name example.com --monitor > examplecom.out 2>&1 &\n```\n\n> Note: The `nohup` command prints a shell job ID and a process ID. Terminate\n> the process with `kill -9 <PID>`.\n\n## Contributing\nContributions are welcome via pull requests.\n\n## Issues\nIf you encounter any problems, please file an\n[issue](https://github.com/MousaZeidBaker/dm53/issues) along with a detailed\ndescription.\n\n## Develop\nActivate virtual environment\n```shell\npoetry shell\n```\n\nInstall dependencies\n```shell\npoetry install --remove-untracked\n```\n\nInstall git hooks\n```shell\npre-commit install --hook-type pre-commit\n```\n\nRun linter\n```shell\nflake8 .\n```\n\nFormat code\n```shell\nblack .\n```\n\nSort imports\n```shell\nisort .\n```\n\nInstall current project from branch\n```shell\npoetry add git+https://github.com/MousaZeidBaker/dm53.git#branch-name\n```\n',
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/dm53',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
