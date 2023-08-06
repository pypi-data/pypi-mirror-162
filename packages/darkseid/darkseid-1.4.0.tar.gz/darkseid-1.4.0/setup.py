# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['darkseid']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'natsort>=8.0.0,<9.0.0',
 'py7zr>=0.18.3,<0.19.0',
 'rarfile>=4.0,<5.0']

extras_require = \
{'docs': ['sphinx-rtd-theme>=0.5.2,<0.6.0', 'sphinxcontrib-napoleon>=0.7,<0.8']}

setup_kwargs = {
    'name': 'darkseid',
    'version': '1.4.0',
    'description': 'A library to interact with comic archives',
    'long_description': '.. image:: https://img.shields.io/pypi/v/darkseid.svg\n    :target: https://pypi.org/project/darkseid/\n\n.. image:: https://img.shields.io/pypi/pyversions/darkseid.svg\n    :target: https://pypi.org/project/darkseid/\n\n.. image:: https://codecov.io/gh/Metron-Project/darkseid/branch/master/graph/badge.svg?token=upXAiHNmcc \n :target: https://codecov.io/gh/Metron-Project/darkseid\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\nDarkseid\n========\n\nA python library to interact with comic archives.\n\nInstallation\n------------\n\nPyPi\n~~~~\n\n.. code:: bash\n\n    $ pip3 install --user darkseid\n\nGitHub\n~~~~~~\n\nInstalling the latest version from Github:\n\n.. code:: bash\n\n    $ git clone https://github.com/Metron-Project/darkseid\n    $ cd darkseid\n    $ python setup.py install\n\nBugs/Requests\n-------------\n\nPlease use the `GitHub issue tracker <https://github.com/Metron-Project/darkseid/issues>`_ to submit bugs or request features.\n\nLicense\n-------\n\nThis project is licensed under the `GPLv3 License <LICENSE>`_.\n',
    'author': 'Brian Pepple',
    'author_email': 'bdpepple@gmail.com',
    'maintainer': 'Brian Pepple',
    'maintainer_email': 'bdpepple@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
