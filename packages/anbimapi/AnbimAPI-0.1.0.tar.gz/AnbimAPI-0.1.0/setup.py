# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['anbimapi']
install_requires = \
['pandas>=1.4.3,<2.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'anbimapi',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Vinicius Mesel',
    'author_email': 'bioinfo.vinicius@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
