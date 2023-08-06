# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pkg_name_validator']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'pkg-name-validator',
    'version': '1.0.0',
    'description': 'A package for making sure your desired package name is available.',
    'long_description': '# pkg_name_validator\n A package for making sure your desired package name is available.\n',
    'author': 'AfterNoon PM',
    'author_email': 'h2o.Drop2010+pypi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tinkering-townsperson/pkg_name_validator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
