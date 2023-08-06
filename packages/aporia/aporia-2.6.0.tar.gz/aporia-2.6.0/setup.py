# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aporia',
 'aporia.core',
 'aporia.core.api',
 'aporia.core.types',
 'aporia.experimental',
 'aporia.inference',
 'aporia.inference.api',
 'aporia.inference.types',
 'aporia.pandas',
 'aporia.pyspark',
 'aporia.pyspark.experimental',
 'aporia.pyspark.training',
 'aporia.training',
 'aporia.training.api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.0,<4.0.0',
 'certifi>=2022.6.15,<2023.0.0',
 'orjson>=3.6.4,<4.0.0',
 'tenacity>=7.0,<9.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.5.0,<2.0.0'],
 ':python_version >= "3.7" and python_version < "3.8"': ['numpy>=1.15,<1.22'],
 ':python_version >= "3.8" and python_version < "4.0"': ['numpy>=1.17.4,<2.0.0'],
 'all': ['pyspark>=3.0,<4.0'],
 'all:python_version >= "3.7" and python_version < "3.8"': ['pandas>=1.0,<1.4'],
 'all:python_version >= "3.8" and python_version < "4.0"': ['pandas>=1.0,<2.0'],
 'pandas:python_version >= "3.7" and python_version < "3.8"': ['pandas>=1.0,<1.4'],
 'pandas:python_version >= "3.8" and python_version < "4.0"': ['pandas>=1.0,<2.0'],
 'pyspark': ['pyspark>=3.0,<4.0'],
 'training:python_version >= "3.7" and python_version < "3.8"': ['pandas>=1.0,<1.4'],
 'training:python_version >= "3.8" and python_version < "4.0"': ['pandas>=1.0,<2.0']}

setup_kwargs = {
    'name': 'aporia',
    'version': '2.6.0',
    'description': 'Aporia SDK',
    'long_description': '# Aporia SDK\n\n## Testing\n\nTo run the tests, first install the library locally:\n```\npip install ".[all]" --upgrade\n```\n\nThen run the tests using `pytest`:\n```\npytest -v\n```\n\nIf you don\'t have Spark installed, skip the pyspark tests:\n```\npytest -v --ignore=tests/pyspark\n```\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aporia-ai/sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
