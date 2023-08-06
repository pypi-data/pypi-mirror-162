# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whocan']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0']

setup_kwargs = {
    'name': 'whocan',
    'version': '0.2.3',
    'description': 'Library for defining and determining access.',
    'long_description': "# Whocan\n\nLibrary for defining and determining access.\n\n## Usage\n\n### YAML usage\n\n```yaml\nstatements:\n- effect: allow\n  actions:\n  - workspace:Create*\n  - workspace:Delete*\n  - workspace:Get*\n  - workspace:List*\n  - workspace:Update*\n  resources:\n  - workspace:individual-${username}\n```\n\n```python\nimport pathlib\nimport whocan\n\npolicy = whocan.Policy.load(pathlib.Path('path-to-file.yaml'))\npolicy.is_allowed(\n    resource='workspaces:individual-my-username',\n    action='workspace:DeletePage',\n    arguments={'username': 'my-username'},\n)\n# True\npolicy.is_allowed(\n    resource='workspaces:individual-a-different-user',\n    action='workspace:DeletePage',\n    arguments={'username': 'my-username'},\n)\n# False\n```\n\n### Pure python usage\n\n```python\nimport whocan\n\nstatement = whocan.Statement(\n    resources=['workspaces:individual-${username}'],\n    actions=[\n        'workspace:Create*',\n        'workspace:Delete*',\n        'workspace:Get*',\n        'workspace:List*',\n        'workspace:Update*',\n    ],\n    effect='allow',\n)\n\npolicy = whocan.Policy(statements=[statement])\npolicy.is_allowed(\n    resource='workspaces:individual-my-username',\n    action='workspace:DeletePage',\n    arguments={'username': 'my-username'},\n)\n# True\npolicy.is_allowed(\n    resource='workspaces:individual-a-different-user',\n    action='workspace:DeletePage',\n    arguments={'username': 'my-username'},\n)\n# False\n```",
    'author': 'Kevin Schiroo',
    'author_email': 'kjschiroo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/kjschiroo/whocan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
