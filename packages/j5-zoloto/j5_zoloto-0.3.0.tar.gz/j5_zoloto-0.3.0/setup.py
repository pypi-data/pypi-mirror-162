# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['j5_zoloto']

package_data = \
{'': ['*']}

install_requires = \
['j5>=1.0.0.rc1,<2.0.0', 'zoloto>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'j5-zoloto',
    'version': '0.3.0',
    'description': 'j5 integration for Zoloto computer vision',
    'long_description': '# j5_zoloto\n\nIntegration between j5 and Zoloto.',
    'author': 'j5 contributors',
    'author_email': 'j5api@googlegroups.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/j5api/j5-zoloto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
