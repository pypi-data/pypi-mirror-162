# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkdocs_code_validator']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3,<4.0', 'mkdocs>=1.0.3,<2.0.0', 'pymdown-extensions>=8.0']

entry_points = \
{'mkdocs.plugins': ['code-validator = '
                    'mkdocs_code_validator.plugin:CodeValidatorPlugin']}

setup_kwargs = {
    'name': 'mkdocs-code-validator',
    'version': '0.1.3',
    'description': 'Checks Markdown code blocks in a MkDocs site against user-defined actions',
    'long_description': '# mkdocs-code-validator\n\n**Checks Markdown code blocks in a [MkDocs][] site against user-defined actions**\n\n[![PyPI](https://img.shields.io/pypi/v/mkdocs-code-validator)](https://pypi.org/project/mkdocs-code-validator/)\n[![License](https://img.shields.io/github/license/oprypin/mkdocs-code-validator)](https://github.com/oprypin/mkdocs-code-validator/blob/master/LICENSE.md)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/oprypin/mkdocs-code-validator/CI)](https://github.com/oprypin/mkdocs-code-validator/actions?query=event%3Apush+branch%3Amaster)\n\n```shell\npip install mkdocs-code-validator\n```\n\n## Usage\n\nActivate the plugin in **mkdocs.yml**. The `identifiers` config is mandatory. And the plugin **doesn\'t work without [pymdownx.superfences][]**:\n\n```yaml\nplugins:\n  - search\n  - code-validator:\n      identifiers:\n        bash:\n          validators:\n            - grep a\nmarkdown_extensions:\n  - pymdownx.superfences\n```\n\nThe above contrived config checks that every <code>```bash</code> code block in the Markdown files of this MkDocs site must contain the letter "a", otherwise a warning will appear.\n\nThe content of each code block is piped as stdin to the command. The exit code of the command is what\'s checked: a non-zero code will produce a warning (which in MkDocs you can make fatal with the `--strict` flag). The output of the command is not used in any way, only preserved on the screen as part of a warning.\n\nYou can add any number of identifiers, and within them any number of `validators` commands, each of them has the ability to produce a warning.\n\nIf stdin is not usable with your command, the input can be passed as a temporary file instead -- that is done if the command contains the exact argument `$<` (which is then replaced with a file path). For the above example, changing the command to `grep a $<` would be equivalent (other than technicalities).\n\nThe commands do *not* allow freeform shell syntax, it\'s just one subprocess to call with its arguments. To explicitly opt into a shell, just run it as (e.g.) `sh -c \'if grep a; then exit 1; fi\'`. Or, with a temporary file: `sh -c \'if grep a "$1"; then exit 1; fi\' $<`.\n\nThe definition of what a code block is is all according to the [pymdownx.superfences][] extension. It must be enabled; the plugin won\'t do anything without it.\n\n\n[mkdocs]: https://www.mkdocs.org/\n[documentation site]: https://oprypin.github.io/mkdocs-code-validator\n[pymdownx.superfences]: https://facelessuser.github.io/pymdown-extensions/extensions/superfences/\n',
    'author': 'Oleh Prypin',
    'author_email': 'oleh@pryp.in',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oprypin/mkdocs-code-validator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
