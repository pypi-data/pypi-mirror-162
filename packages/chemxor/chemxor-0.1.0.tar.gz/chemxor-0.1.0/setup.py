# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['chemxor',
 'chemxor.cli',
 'chemxor.config',
 'chemxor.data',
 'chemxor.model',
 'chemxor.pipelines',
 'chemxor.routes',
 'chemxor.schema',
 'chemxor.service']

package_data = \
{'': ['*'],
 'chemxor.config': ['base/*', 'base/catalog/*', 'base/parameters/*', 'local/*']}

install_requires = \
['Flask>=2.1.2,<3.0.0',
 'ase>=3.22.1,<4.0.0',
 'dask>=2022.7.1,<2023.0.0',
 'gensim>=4.1.2,<5.0.0',
 'logzero>=1.7.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'nltk>=3.6.7,<4.0.0',
 'onnx>=1.11.0,<2.0.0',
 'pandas==1.3.4',
 'protobuf==3.19.1',
 'pydantic[dotenv]>=1.8.2,<2.0.0',
 'pytorch-lightning>=1.6.1,<2.0.0',
 'rdkit-pypi>=2022.3.1,<2023.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy==1.7.3',
 'tenseal>=0.3.11,<0.4.0',
 'torch[cpu]>=1.10.0,<2.0.0',
 'torchani>=2.2,<3.0',
 'torchvision>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['chemxor = chemxor.cli.main:main']}

setup_kwargs = {
    'name': 'chemxor',
    'version': '0.1.0',
    'description': 'Privacy Preserving AI/ML for Drug Discovery',
    'long_description': None,
    'author': 'Ankur Kumar',
    'author_email': 'ank@leoank.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
