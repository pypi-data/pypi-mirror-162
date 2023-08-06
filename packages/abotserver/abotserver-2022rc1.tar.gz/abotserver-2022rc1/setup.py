# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['abotserver', 'abotserver.providers', 'abotserver.routers']

package_data = \
{'': ['*']}

install_requires = \
['aliyun-python-sdk-core>=2.13.36,<3.0.0',
 'aliyun-python-sdk-nlp-automl>=0.0.9,<0.0.10',
 'fastapi>=0.79.0,<0.80.0',
 'gunicorn>=20.1.0,<21.0.0',
 'lockfile>=0.12.2,<0.13.0',
 'psutil>=5.9.1,<6.0.0',
 'python-daemon>=2.3.0,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'uvicorn>=0.18.2,<0.19.0']

entry_points = \
{'console_scripts': ['abotserver = abotserver.cmd:cli']}

setup_kwargs = {
    'name': 'abotserver',
    'version': '2022rc1',
    'description': '',
    'long_description': None,
    'author': 'fineartit',
    'author_email': 'fineartit@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
