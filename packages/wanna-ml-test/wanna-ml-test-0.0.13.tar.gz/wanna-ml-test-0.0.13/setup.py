# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wanna', 'wanna.cli']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyGithub>=1.55,<2.0',
 'PyYAML>=5.4.0,<6.0.0',
 'case-converter>=1.0.2,<2.0.0',
 'checksumdir>=1.2.0,<2.0.0',
 'cookiecutter>=1.7.3,<2.0.0',
 'cron-validator>=1.0.6,<2.0.0',
 'email-validator>=1.2.1,<2.0.0',
 'emoji>=1.7.0,<2.0.0',
 'gitpython>=3.1.27,<4.0.0',
 'halo>=0.0.31,<0.0.32',
 'importlib-metadata>=4.0,<5.0',
 'kfp>=1.8.12,<2.0.0',
 'merge-args>=0.1.4,<0.2.0',
 'packaging>=21.3,<22.0',
 'pandas>=1.3.3,<2.0.0',
 'pathvalidate>=2.5.0,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-on-whales>=0.43.0,<0.44.0',
 'pyyaml-include>=1.3,<2.0',
 'smart-open[gcs]>=6.0,<7.0',
 'treelib>=1.6.1,<2.0.0',
 'typer>=0.4.1,<0.5.0',
 'waiting>=1.4.1,<2.0.0']

entry_points = \
{'console_scripts': ['wanna = wanna.cli.__main__:app']}

setup_kwargs = {
    'name': 'wanna-ml-test',
    'version': '0.0.13',
    'description': 'CLI tool for managing ML projects on Vertex AI',
    'long_description': None,
    'author': 'Joao Da Silva',
    'author_email': 'joao.silva1@avast.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
