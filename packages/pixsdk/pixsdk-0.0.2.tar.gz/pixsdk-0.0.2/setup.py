# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pixsdk', 'pixsdk.plugins']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24,<4.0.0',
 'Jinja2==3.0.3',
 'PyGithub>=1.55,<2.0',
 'click>=8.1.3,<9.0.0',
 'requests>=2.27.1,<3.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0']

entry_points = \
{'console_scripts': ['pix = pixsdk.cli:cli']}

setup_kwargs = {
    'name': 'pixsdk',
    'version': '0.0.2',
    'description': 'Used to run pix scripts.',
    'long_description': None,
    'author': 'Dan Clayton',
    'author_email': 'dan@azwebmaster.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
