# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ncem',
 'ncem.api',
 'ncem.api.train',
 'ncem.estimators',
 'ncem.interpretation',
 'ncem.models',
 'ncem.models.layers',
 'ncem.train',
 'ncem.unit_test',
 'ncem.utils']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<4.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'diffxpy>=0.7.4,<0.8.0',
 'docrep>=0.3.2,<0.4.0',
 'louvain>=0.7.0,<0.8.0',
 'matplotlib>=3.4.2,<4.0.0',
 'patsy>=0.5.1,<0.6.0',
 'rich>=10.1.0,<11.0.0',
 'scanpy>=1.7.2,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'squidpy>=1.0.0,<2.0.0',
 'tensorflow>=2.5.0,<3.0.0']

entry_points = \
{'console_scripts': ['ncem = ncem.__main__:main']}

setup_kwargs = {
    'name': 'ncem',
    'version': '0.1.4',
    'description': 'ncem. Learning cell communication from spatial graphs of cells.',
    'long_description': 'ncem\n===========================\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/ncem.svg\n   :target: https://pypi.org/project/ncem/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ncem\n   :target: https://pypi.org/project/ncem\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/theislab/ncem\n   :target: https://opensource.org/licenses/BSD-3-Clause\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/ncem/latest.svg?label=Read%20the%20Docs\n   :target: https://ncem.readthedocs.io/\n   :alt: Read the documentation at https://ncem.readthedocs.io/\n.. |Build| image:: https://github.com/theislab/ncem/workflows/Build%20ncem%20Package/badge.svg\n   :target: https://github.com/theislab/ncem/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/theislab/ncem/workflows/Run%20ncem%20Tests/badge.svg\n   :target: https://github.com/theislab/ncem/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/theislab/ncem/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/theislab/ncem\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n.. image:: https://raw.githubusercontent.com/theislab/ncem/main/docs/_static/img/concept.png\n   :target: https://raw.githubusercontent.com/theislab/ncem/main/docs/_static/img/concept.png\n   :align: center\n   :alt: ncem concept\n   :width: 1000px\n\n\nFeatures\n--------\nncem_ is a model repository in a single python package for the manuscript *Fischer, D. S., Schaar, A. C. and Theis, F. Learning cell communication from spatial\ngraphs of cells. 2021.* (preprint_)\n\n\nInstallation\n------------\n\nYou can install *ncem* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install ncem\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. _ncem: https://ncem.readthedocs.io\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Usage: https://ncem.readthedocs.io/en/latest/usage.html\n.. _preprint: https://www.biorxiv.org/content/10.1101/2021.07.11.451750v1\n',
    'author': 'Anna C. Schaar',
    'author_email': 'anna.schaar@helmholtz-muenchen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/ncem',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
