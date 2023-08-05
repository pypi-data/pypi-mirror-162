# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_update']

package_data = \
{'': ['*']}

install_requires = \
['awesome-pattern-matching>=0.24.3,<0.25.0',
 'decorator>=5.1.1,<6.0.0',
 'typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'poetry-update',
    'version': '0.0.0',
    'description': 'poetry-update - a tool/plugin that updates dependencies and dumps their version in both poetry.lock and pyproject.toml files.',
    'long_description': '<p align="center">\n  <a href="https://opensource.org/licenses/MIT">\n    <img alt="license" src="https://img.shields.io/pypi/l/poetry-update?logo=opensourceinitiative">\n  </a>\n  <a href="https://pypi.org/project/poetry-update">\n    <img alt="python" src="https://img.shields.io/pypi/pyversions/poetry-update?logo=python">\n  </a>\n  <a href="https://pypi.org/project/poetry-update">\n    <img alt="pypi" src="https://img.shields.io/pypi/v/poetry-update?logo=pypi">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/releases">\n    <img alt="release" src="https://img.shields.io/github/v/release/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://www.sphinx-doc.org/en/master">\n    <img alt="sphinx" src="https://img.shields.io/badge/made_with-Sphinx-1f425f.svg?logo=readthedocs">\n  </a>\n  <a href="https://numpydoc.readthedocs.io/en/latest/format.html">\n    <img alt="numpydoc" src="https://img.shields.io/badge/docstrings-numpy-1f425f.svg?logo=numpy">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://github.com/psf/black">\n    <img alt="black" src="https://img.shields.io/badge/code_style-black-black.svg?logo=windowsterminal">\n  </a>\n  <a href="https://pycqa.github.io/isort/index.html">\n    <img alt="isort" src="https://img.shields.io/badge/imports-isort-black.svg?logo=windowsterminal">\n  </a>\n  <a href="https://wemake-python-stylegui.de/en/latest/index.html">\n    <img alt="wemake" src="https://img.shields.io/badge/style-wemake-black.svg?logo=windowsterminal">\n  </a>\n  <a href="https://mypy.readthedocs.io/en/stable/index.html">\n    <img alt="mypy" src="https://img.shields.io/badge/mypy-checked-success.svg?logo=python">\n  </a>\n  <a href="https://github.com/pyupio/safety">\n    <img alt="safety" src="https://img.shields.io/badge/safety-checked-success.svg?logo=windowsterminal">\n  </a>\n  <a href="https://github.com/semantic-release/semantic-release">\n    <img alt="semantic_release" src="https://img.shields.io/badge/semantic_release-angular-e10079?logo=semantic-release">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://github.com/dependabot">\n    <img alt="dependabot" src="https://img.shields.io/badge/dependabot-enable-success?logo=Dependabot">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/actions/workflows/integration.yaml">\n    <img alt="integration" src="https://img.shields.io/github/workflow/status/volopivoshenko/poetry-update/CI?label=CI&logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/actions/workflows/deployment.yaml">\n    <img alt="deployment" src="https://img.shields.io/github/workflow/status/volopivoshenko/poetry-update/CD?label=CD&logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/actions/workflows/codeql.yaml">\n    <img alt="codeql" src="https://img.shields.io/github/workflow/status/volopivoshenko/poetry-update/CodeQL?label=codeQL&logo=github">\n  </a>\n  <a href="https://poetry-update.readthedocs.io/en/latest">\n    <img alt="docs" src="https://img.shields.io/readthedocs/poetry-update?logo=readthedocs">\n  </a>\n  <a href="https://pypi.org/project/poetry-update">\n    <img alt="wheel" src="https://img.shields.io/pypi/wheel/poetry-update?logo=pypi">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://codecov.io/gh/volopivoshenko/poetry-update">\n    <img alt="coverage" src="https://img.shields.io/codecov/c/gh/volopivoshenko/poetry-update?logo=codecov&token=yyck08xfTN"/>\n  </a>\n  <a href="https://lgtm.com/projects/g/volopivoshenko/poetry-update/alerts/">\n    <img alt="alerts" src="https://img.shields.io/lgtm/alerts/github/volopivoshenko/poetry-update?logo=lgtm"/>\n  </a>\n  <a href="https://lgtm.com/projects/g/volopivoshenko/poetry-update/context:python">\n    <img alt="grade" src="https://img.shields.io/lgtm/grade/python/github/volopivoshenko/poetry-update?logo=lgtm"/>\n  </a>\n  <a href="https://codeclimate.com/github/volopivoshenko/poetry-update/maintainability">\n    <img alt="codeclimate" src="https://img.shields.io/codeclimate/maintainability/volopivoshenko/poetry-update?logo=codeclimate">\n  </a>\n  <a href="https://pypi.org/project/poetry-update">\n    <img alt="downloads" src="https://img.shields.io/pypi/dm/poetry-update?logo=pypi">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/">\n    <img alt="stars" src="https://img.shields.io/github/stars/volopivoshenko/poetry-update?logo=github">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://github.com/volopivoshenko/poetry-update/issues">\n    <img alt="issues" src="https://img.shields.io/github/issues/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/issues">\n    <img alt="issues" src="https://img.shields.io/github/issues-closed/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/pulls">\n    <img alt="pr" src="https://img.shields.io/github/issues-pr/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/pulls">\n    <img alt="pr" src="https://img.shields.io/github/issues-pr-closed/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/graphs/contributors">\n    <img alt="contributors" src="https://img.shields.io/github/contributors/volopivoshenko/poetry-update?logo=github">\n  </a>\n  <a href="https://github.com/volopivoshenko/poetry-update/commits/main">\n    <img alt="commit" src="https://img.shields.io/github/last-commit/volopivoshenko/poetry-update?logo=github">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://www.buymeacoffee.com/volopivoshenko" target="_blank">\n    <img alt="buymeacoffee" src="https://img.shields.io/badge/buy_me_-a_coffee-ff6964?logo=buymeacoffee">\n  </a>\n</p>\n\n- [Overview](#overview)\n- [Installation](#installation)\n    - [Optional dependencies](#optional-dependencies)\n\n# Overview\n\n# Installation\n\n## Optional dependencies\n',
    'author': 'Volodymyr Pivoshenko',
    'author_email': 'volodymyr.pivoshenko@gmail.com',
    'maintainer': 'Volodymyr Pivoshenko',
    'maintainer_email': 'volodymyr.pivoshenko@gmail.com',
    'url': 'https://poetry-update.readthedocs.io/en/latest',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
