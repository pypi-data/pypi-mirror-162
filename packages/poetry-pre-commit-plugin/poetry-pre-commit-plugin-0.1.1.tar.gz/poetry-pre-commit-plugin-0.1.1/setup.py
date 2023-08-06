# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_pre_commit_plugin']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0b1,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['poetry-pre-commit-plugin = '
                               'poetry_pre_commit_plugin.plugin:PreCommitPlugin']}

setup_kwargs = {
    'name': 'poetry-pre-commit-plugin',
    'version': '0.1.1',
    'description': 'Poetry plugin for automatically installing pre-commit hook when it is added to a project',
    'long_description': "# Poetry pre-commit Plugin\n\nA [Poetry](https://python-poetry.org/) plugin for automatically installing git\npre-commit hooks whenever `pre-commit` is specified as a dependency of the\nproject.\n\n## Motivation\n\nPersonally I find that running `pre-commit install` every time I start working\non a new repository is very easy to forget - there have been numerous occasions\nwhere I'd forget this step, commit some changes only to be surprised later on\nby failing CI checks 😅 This plugin aims to solve this issue by doing\nthis small step for me automatically behind the scenes.\n\n## Installation\n\nThe plugin requires Poetry version `1.2.0b1` or above. Since this is still a\npre-release version, you have to specify it explicitly when installing:\n\n```\ncurl -sSL https://install.python-poetry.org | python3.9 - --version 1.2.0b3\n```\n\nOnce a valid version of Poetry is set up, you can install the plugin like so:\n\n```\npoetry self add poetry-pre-commit-plugin\n```\n\nFor more in-depth information, please refer to\n[Poetry's docs](https://python-poetry.org/docs/master/plugins/).\n\n## Usage\n\nThere's no way to use this plugin explicitly - it will work behind the scenes\nafter you run either `poetry install` or `poetry add`. In either of those cases,\nthe plugin will check the following conditions:\n\n1. Is the project inside a git repository?\n2. Is `pre-commit` listed as a dependency of the project (or, in the case of\n   `poetry add` - was it just added)?\n3. Has the pre-commit hook **not** been activated yet (i.e. the file\n   `.git/hooks/pre-commit` does not exist)?\n\nIf all conditions are met, the plugin will run `pre-commit install` for you.\n",
    'author': 'Vytautas Strimaitis',
    'author_email': 'vstrimaitis@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/vstrimaitis/poetry-pre-commit-plugin',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
