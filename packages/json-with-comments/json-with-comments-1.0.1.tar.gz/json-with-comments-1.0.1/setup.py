# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsonc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'json-with-comments',
    'version': '1.0.1',
    'description': 'JSON with Comments for Python',
    'long_description': '# JSON with Comments for Python\n[![pypi version](https://img.shields.io/pypi/v/json-with-comments.svg)](https://pypi.python.org/project/json-with-comments)\n[![Python package](https://github.com/n-takumasa/json-with-comments/actions/workflows/python-package.yml/badge.svg)](https://github.com/n-takumasa/json-with-comments/actions/workflows/python-package.yml)\n[![Python Versions](https://img.shields.io/pypi/pyversions/json-with-comments.svg)](https://pypi.org/project/json-with-comments/)\n\n## Features\n* Remove single line (`//`) and block comments (`/* */`)\n* Remove trailing commas from arrays and objects\n\n## Usage\n\n```sh\npip install json-with-comments\n```\n\n```py\n>>> import jsonc\n>>> jsonc.loads("{// comment \\n}")\n{}\n>>> jsonc.loads("{/* comment */}")\n{}\n>>> jsonc.loads(\'{"spam": "ham // egg" /* comment */}\')\n{\'spam\': \'ham // egg\'}\n>>> jsonc.loads(\'{"spam": /* comment */"ham /* egg */"}\')\n{\'spam\': \'ham /* egg */\'}\n```\nAnd just like `json` module\n',
    'author': 'Takumasa Nakamura',
    'author_email': 'n.takumasa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/n-takumasa/json-with-comments',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
