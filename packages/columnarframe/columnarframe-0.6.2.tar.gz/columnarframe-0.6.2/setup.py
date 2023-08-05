# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['columnarframe']

package_data = \
{'': ['*']}

install_requires = \
['openpyxl>=3.0.7,<4.0.0', 'pyarrow>=3.0.0,<4.0.0', 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'columnarframe',
    'version': '0.6.2',
    'description': '',
    'long_description': '# ColumnarFrame\n\nカラムベースでデータを扱うためのライブラリです。\nある程度Pandasのように操作できるような形を目指しています。\n\nThis is a library for handling column-based data.\nIt is intended to be operated like Pandas to some extent.\n\n## Memo\n\n* unittest\n\n```\npoetry run python -m unittest discover\n```\n\n* build\n\n```\npoetry build\n```\n\n* publish(Test)\n\n```\npoetry publish -r testpypi\n```\n\n* public(real)\n\n```\npoetry publish\n```\n\n* lib install\n\n```\npoetry add xxxx\n```\n\n',
    'author': 'tamuto',
    'author_email': 'tamuto@infodb.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tamuto/columnarframe',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
