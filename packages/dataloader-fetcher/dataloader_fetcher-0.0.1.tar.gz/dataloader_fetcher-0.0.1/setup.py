# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataloader_fetcher']

package_data = \
{'': ['*']}

install_requires = \
['scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'setuptools>=63.2.0,<64.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'torch>=1.10.0,<2.0.0',
 'torchvision>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'dataloader-fetcher',
    'version': '0.0.1',
    'description': 'Dataloader for PyTorch',
    'long_description': '# Dataloader\n\nA python module for loading datasets from \n\n* Scikit-learn\n* Torchvision\n\nIt supports loading\n\n* Wine\n* Iris\n* MNIST datasets\n\nDefaults to loading IRIS.\n\nThis module also performs pre-processing relevant to each data set type.\nIt handles categorical data for tabular sets like Iris and it performs transforms for images in the computer vision dataset like MNIST.\n\n## Install\n\nUsing a package manager\n```\n$ poetry add dataloader-fetcher\n```\n\n## Example usage\n\n```\nfetcher = DataloaderFetcher()\ntrain_loader = fetcher.train_loader(name="Iris")\ntest_loader  = fetcher.test_loader(name="Iris")\n```',
    'author': '"Frank Kelly", "Zabil CM"',
    'author_email': None,
    'maintainer': 'Frank Kelly',
    'maintainer_email': None,
    'url': 'https://github.com/taimatsudev/dataloader/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.0,<3.11',
}


setup(**setup_kwargs)
