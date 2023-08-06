# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coretypes', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>=2.1.0,<3.0.0', 'numpy>=1.20,<2.0']

extras_require = \
{'dev': ['black>=22.3.0,<23.0.0',
         'tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.3.0,<2.0.0',
         'mkdocs-include-markdown-plugin>=3.2.3,<4.0.0',
         'mkdocs-material>=8.1.11,<9.0.0',
         'livereload>=2.6.3,<3.0.0',
         'mkdocstrings>=0.18.0,<0.19.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'mike>=1.1.2,<2.0.0'],
 'test': ['black>=22.3.0,<23.0.0',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'zillionare-core-types',
    'version': '0.5.1',
    'description': 'core types definition shared by zillionare.',
    'long_description': '# zillionare core types\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/zillionare_core_types">\n    <img src="https://img.shields.io/pypi/v/zillionare_core_types.svg"\n        alt = "Release Status">\n</a>\n\n</p>\n\n\n定义了zillionare平台中多数项目/模块需要使用的核心数据类型，比如FrameType, SecuirityType, bars_dtype， BarsArray等。\n\n* Free software: MIT\n* Documentation: <https://zillionare-core-types.readthedocs.io>\n\n\n## Features\n\n* 提供了FrameType, SecurityType, bars_dtype等数据类型\n* 提供了BarsArray, BarsPanel, BarsWithLimitArray等type annotation （type hint)类型\n* 提供了quote_fetcher接口类。\n\n## Credits\n\n本项目使用[ppw](https://zillionare.github.io/python-project-wizard/)创建，并遵循ppw定义的代码风格和质量规范。\n',
    'author': 'Aaron Yang',
    'author_email': 'code@jieyu.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zillionare/zillionare_core_types',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
