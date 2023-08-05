# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skqulacs', 'skqulacs.circuit', 'skqulacs.qnn', 'skqulacs.qsvm']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.0,<2.0.0',
 'qulacs-osaka>=0.4.2,<0.5.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'skqulacs',
    'version': '0.3.0',
    'description': 'scikit-qulacs is a library for quantum neural network. This library is based on qulacs and named after scikit-learn.',
    'long_description': '# scikit-qulacs\n\n[![Unit test](https://github.com/Qulacs-Osaka/scikit-qulacs/actions/workflows/unittest.yml/badge.svg?branch=main)](https://github.com/Qulacs-Osaka/scikit-qulacs/actions/workflows/unittest.yml)\n[![Build and Deploy Documentation](https://github.com/Qulacs-Osaka/scikit-qulacs/actions/workflows/doc.yml/badge.svg?branch=main)](https://github.com/Qulacs-Osaka/scikit-qulacs/actions/workflows/doc.yml)\n[![codecov](https://codecov.io/gh/Qulacs-Osaka/scikit-qulacs/branch/main/graph/badge.svg?token=8RCM3B9KQ8)](https://codecov.io/gh/Qulacs-Osaka/scikit-qulacs)\n[![PyPI version](https://badge.fury.io/py/skqulacs.svg)](https://badge.fury.io/py/skqulacs)\n[![MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)\n\nscikit-qulacs is a library for quantum neural network. This library is based on qulacs and named after scikit-learn.\n\n## Installation\n### pip\n```bash\npip install skqulacs\n```\n\n### Build from Source\nInstall [poetry](https://python-poetry.org/docs/) before building package.\n```bash\ngit clone https://github.com/Qulacs-Osaka/scikit-qulacs.git\ncd scikit-qulacs\npoetry install\n```\n\n## Documentation\nTutorial: [scikit-qulacs チュートリアル](./doc/source/notebooks/0_tutorial.ipynb) (Only Japanese version is available now)\n\nAPI Documentation and example notebooks: [scikit-qulacs documentation](https://qulacs-osaka.github.io/scikit-qulacs/index.html)\n',
    'author': 'Qulacs-Osaka',
    'author_email': 'qulacs.osaka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Qulacs-Osaka/scikit-qulacs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
