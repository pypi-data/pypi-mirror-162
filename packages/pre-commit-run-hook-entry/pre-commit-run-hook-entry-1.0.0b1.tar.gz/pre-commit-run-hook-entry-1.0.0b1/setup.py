# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pre_commit_run_hook_entry']

package_data = \
{'': ['*']}

install_requires = \
['pre-commit>=2.19.0,<3.0.0']

entry_points = \
{'console_scripts': ['pre-commit-run-black-entry = '
                     'pre_commit_run_hook_entry.cli:main_black',
                     'pre-commit-run-hook-entry = '
                     'pre_commit_run_hook_entry.cli:main',
                     'pre-commit-which-hook-entry = '
                     'pre_commit_run_hook_entry.cli:main_which']}

setup_kwargs = {
    'name': 'pre-commit-run-hook-entry',
    'version': '1.0.0b1',
    'description': 'Run pre-commit hook entry. Allow to run pre-commit hooks for text editor formatting / linting needs',
    'long_description': '=========================\npre-commit-run-hook-entry\n=========================\n\n.. image:: https://github.com/playpauseandstop/pre-commit-run-hook-entry/workflows/ci/badge.svg\n    :target: https://github.com/playpauseandstop/pre-commit-run-hook-entry/actions?query=workflow%3A%22ci%22\n    :alt: CI Workflow\n\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n    :target: https://github.com/pre-commit/pre-commit\n    :alt: pre-commit\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\n.. image:: https://img.shields.io/pypi/v/pre-commit-run-hook-entry.svg\n    :target: https://pypi.org/project/pre-commit-run-hook-entry/\n    :alt: Latest Version\n\n.. image:: https://img.shields.io/pypi/pyversions/pre-commit-run-hook-entry.svg\n    :target: https://pypi.org/project/pre-commit-run-hook-entry/\n    :alt: Python versions\n\n.. image:: https://img.shields.io/pypi/l/pre-commit-run-hook-entry.svg\n    :target: https://github.com/playpauseandstop/pre-commit-run-hook-entry/blob/main/LICENSE\n    :alt: BSD License\n\n.. image:: https://coveralls.io/repos/playpauseandstop/pre-commit-run-hook-entry/badge.svg?branch=main&service=github\n    :target: https://coveralls.io/github/playpauseandstop/pre-commit-run-hook-entry\n    :alt: Coverage\n\nRun `pre-commit`_ hook entry. Allow to run pre-commit hooks for text editor\nformatting / linting needs.\n\n.. _`pre-commit`: https://pre-commit.com/\n\nDanger Zone\n===========\n\n**IMPORTANT:** This is highly experimental tool as `pre-commit internals does\nnot intend to be used in other scripts\n<https://github.com/pre-commit/pre-commit/issues/1468#issuecomment-640699437>`_.\nIt might be broken after new pre-commit release.\n\n**TO USE WITH CAUTION!**\n\nRequirements\n============\n\n- `Python <https://www.python.org/>`_ 3.7 or later\n- `pre-commit`_ 2.19.0 or later\n\nLicense\n=======\n\n``pre-commit-run-hook-entry`` is licensed under the terms of\n`BSD-3-Clause </LICENSE>`_ license.\n\nInstallation\n============\n\n.. code-block:: bash\n\n    pip install pre-commit-run-hook-entry\n\nUsage\n=====\n\n.. code-block:: bash\n\n    pre-commit-run-hook-entry HOOK [ARGS]\n    pre-commit-which-hook-entry HOOK\n\nPrerequisites\n-------------\n\n``pre-commit-run-hook-entry`` only works in directories, where\n``pre-commit run --all HOOK`` is executable.\n\nVS Code Integration\n-------------------\n\nExample below illustrates how to configure VS Code to use black, flake8 &\nmypy pre-commit hooks for formatting & linting,\n\n.. code-block:: json\n\n    {\n        "python.formatting.provider": "black",\n        "python.formatting.blackPath": "pre-commit-run-hook-entry",\n        "python.formatting.blackArgs": ["black"],\n        "python.linting.enabled": true,\n        "python.linting.flake8Enabled": true,\n        "python.linting.flake8Path": "pre-commit-run-hook-entry",\n        "python.linting.flake8Args": ["flake8"],\n        "python.linting.mypyEnabled": true,\n        "python.linting.mypyPath": "pre-commit-run-hook-entry",\n        "python.linting.mypyArgs": ["mypy"]\n    }\n\nSublime Text 3 Integration\n--------------------------\n\nsublack\n~~~~~~~\n\nFrom one point `sublack <https://github.com/jgirardet/sublack/>`__ has builtin\npre-commit integration, but it seems do not respect settings from\n``pyproject.toml``, to fix this use ``pre-commit-run-black-entry`` as\n``sublack.black_command``,\n\n.. code-block:: json\n\n    {\n        "sublack.black_command": "pre-commit-run-black-entry"\n    }\n\n\nSublimeLinter-flake8\n~~~~~~~~~~~~~~~~~~~~\n\n.. code-block:: json\n\n    {\n        "SublimeLinter.linters.flake8.executable": "pre-commit-run-hook-entry",\n        "SublimeLinter.linters.flake8.args": ["--", "flake8"]\n    }\n\n\nSublimeLinter-contrib-mypy\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n.. code-block:: json\n\n    {\n        "SublimeLinter.linters.mypy.executable": "pre-commit-run-hook-entry",\n        "SublimeLinter.linters.mypy.args": ["--", "mypy"]\n    }\n\nSublimeJsPrettier\n~~~~~~~~~~~~~~~~~\n\nFirst, you need to find out path to prettier hook entry with,\n\n.. code-block:: bash\n\n    pre-commit-which-hook-entry prettier\n\nThen, paste command output (``<OUTPUT>``) into plugin config,\n\n.. code-block:: json\n\n    {\n        "js_prettier": {\n            "prettier_cli_path": "<OUTPUT>"\n        }\n    }\n\nSublimeLinter-eslint\n~~~~~~~~~~~~~~~~~~~~\n\nFirst, you need to find out path to eslint hook entry with,\n\n.. code-block:: bash\n\n    pre-commit-which-hook-entry eslint\n\nThen, paste command output (``<OUTPUT>``) into plugin config,\n\n.. code-block:: json\n\n    {\n        "SublimeLinter.linters.eslint.executable": "<OUTPUT>",\n        "SublimeLinter.linters.eslint.env": {\n            "NODE_PATH": "<OUTPUT>/../../lib/node_modules"\n        }\n    }\n\n**IMPORTANT:** If you\'re using any ``additionalDependencies`` for eslint hook,\nyou need to configure ``NODE_PATH``, so plugin will be able to find out given\ndependencies.\n\nIssues & Feature Requests\n=========================\n\nFeel free to submit new issue or feature request `at GitHub\n<https://github.com/playpauseandstop/pre-commit-run-hook-entry/issues>`_\n',
    'author': 'Igor Davydenko',
    'author_email': 'iam@igordavydenko.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://igordavydenko.com/projects/#pre-commit-run-hook-entry',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
