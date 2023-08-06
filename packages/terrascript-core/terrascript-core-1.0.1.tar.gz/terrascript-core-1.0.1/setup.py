# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['terrascript',
 'terrascript.core',
 'terrascript.core.ast',
 'terrascript.core.lang',
 'terrascript.core.terraform',
 'terrascript.core.terraform.backend']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'click>=8.0.1,<9.0.0',
 'pybars3>=0.9.7,<0.10.0',
 'pydash>=5.0.2,<6.0.0',
 'pytest-asyncio>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'terrascript-core',
    'version': '1.0.1',
    'description': '',
    'long_description': None,
    'author': 'csylaios',
    'author_email': 'chris.sylaios@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
