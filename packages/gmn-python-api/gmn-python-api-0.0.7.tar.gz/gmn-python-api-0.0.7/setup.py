# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gmn_python_api']

package_data = \
{'': ['*'], 'gmn_python_api': ['data_models/*']}

install_requires = \
['avro-validator==1.0.9',
 'avro==1.11.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'click==8.0.4',
 'numpy>1.20.3',
 'pandas>=1.1.0,<=1.3.5',
 'pandavro==1.6.0',
 'requests>=2.21.0,<3.0.0',
 'types-requests>=2.27.8,<3.0.0']

entry_points = \
{'console_scripts': ['gmn-python-api = gmn_python_api.__main__:main']}

setup_kwargs = {
    'name': 'gmn-python-api',
    'version': '0.0.7',
    'description': 'GMN Python API',
    'long_description': 'GMN Python API\n==============\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/gmn-python-api.svg\n   :target: https://pypi.org/project/gmn-python-api/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/gmn-python-api.svg\n   :target: https://pypi.org/project/gmn-python-api/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/gmn-python-api\n   :target: https://pypi.org/project/gmn-python-api\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/gmn-data-platform/gmn-python-api\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/gmn-python-api/latest.svg?label=Read%20the%20Docs\n   :target: https://gmn-python-api.readthedocs.io/\n   :alt: Read the documentation at https://gmn-python-api.readthedocs.io/\n.. |Tests| image:: https://github.com/gmn-data-platform/gmn-python-api/workflows/Tests/badge.svg\n   :target: https://github.com/gmn-data-platform/gmn-python-api/actions?query=workflow%3ATests+branch%3Amain\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/gmn-data-platform/gmn-python-api/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/gmn-data-platform/gmn-python-api\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nPython library for accessing open `Global Meteor Network`_ (GMN) meteor trajectory `data`_.\nGlobal meteor data is generated using a network of low-light cameras pointed towards the night sky.\nMeteor properties (radiants, orbits, magnitudes and masses) are produced by the GMN and are available through this library.\n\n.. image:: https://raw.githubusercontent.com/gmn-data-platform/gmn-python-api/main/screenshot.png\n  :alt: Data screenshot\n\n|\n\n`Demo on Google Colab`_\n\nFeatures\n--------\n\n* Listing available daily and monthly csv trajectory summary files from the `GMN data directory`_.\n\n* Downloading specific daily and monthly csv trajectory summary files from the data directory.\n\n* Functions for loading the data directory trajectory summary data into Pandas_ DataFrames or Numpy_ arrays.\n\n* Functions for retrieving meteor summary data from the future GMN Data Store using the GMN REST API.\n\n* Functions for loading REST API meteor summary data into Pandas_ DataFrames or Numpy_ arrays.\n\n* Functions for retrieving the current meteor trajectory schema in AVRO_ format.\n\n* Functions for retrieving available IAU_ registered meteor showers.\n\nRequirements\n------------\n\n* Python 3.7.1+, 3.8, 3.9 or 3.10\n\n\nInstallation\n------------\n\nYou can install *GMN Python API* via pip_ from `PyPI`_:\n\n.. code:: console\n\n   $ pip install gmn-python-api\n\nOr install the latest development code, through TestPyPI_ or directly from GitHub_ via pip_:\n\n.. code:: console\n\n   $ pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple gmn-python-api==<version>\n   Or\n   $ pip install git+https://github.com/gmn-data-platform/gmn-python-api\n\nThere is also a `development Google Colab notebook`_.\n\nSee the Troubleshooting_ section if you encounter installation issues.\n\nUsage\n-----\n\nSimple meteor analysis example:\n\n.. code:: python\n\n   from datetime import datetime\n   from gmn_python_api.data_directory import get_daily_file_content_by_date\n   from gmn_python_api.meteor_summary_reader import read_meteor_summary_csv_as_dataframe\n\n   trajectory_summary_file_content = get_daily_file_content_by_date(datetime(2019, 7, 24))\n   trajectory_summary_dataframe = read_meteor_summary_csv_as_dataframe(\n       trajectory_summary_file_content,\n       csv_data_directory_format=True,\n   )\n\n   print(f"{trajectory_summary_dataframe[\'Vgeo (km/s)\'].max()} km/s "\n          "was the fastest geostationary velocity out of all meteors for that day.")\n   # 65.38499 km/s was the fastest geostationary velocity out of all meteors (24th of July 2019).\n\n   print(f"{trajectory_summary_dataframe.loc[trajectory_summary_dataframe[\'IAU (code)\'] == \'PER\'].shape[0]} "\n          "meteors were estimated to be part of the Perseids shower.")\n   # 8 meteors were estimated to be part of the Perseids shower (24th of July 2019).\n\n   print(f"Station {trajectory_summary_dataframe[\'Num (stat)\'].mode().values[0]} "\n          "recorded the highest number of meteors.")\n   # Station 2 recorded the highest number of meteors (24th of July 2019).\n\nPlease see the Usage_ and `API Reference`_ section for more details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*GMN Python API* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\n`Hypermodern Python Cookiecutter`_ template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/project/gmn-python-api/\n.. _TestPyPI: https://test.pypi.org/project/gmn-python-api/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/gmn-data-platform/gmn-python-api/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: https://gmn-python-api.readthedocs.io/en/latest/contributing.html\n.. _Usage: https://gmn-python-api.readthedocs.io/en/latest/usage.html\n.. _API Reference: https://gmn-python-api.readthedocs.io/en/latest/autoapi/gmn_python_api/index.html\n.. _Global Meteor Network: https://globalmeteornetwork.org/\n.. _data: https://globalmeteornetwork.org/data/\n.. _Demo on Google Colab: https://colab.research.google.com/github/gmn-data-platform/gmn-data-endpoints/blob/dc25444cb98693081443bb31e8f6b2abbed3fde2/gmn_data_analysis_template.ipynb\n.. _GMN data directory: https://globalmeteornetwork.org/data/traj_summary_data/\n.. _Pandas: https://pandas.pydata.org/\n.. _Numpy: https://numpy.org/\n.. _GitHub: https://github.com/gmn-data-platform/gmn-python-api\n.. _Troubleshooting: https://gmn-python-api.readthedocs.io/en/latest/troubleshooting.html\n.. _development Google Colab notebook: https://colab.research.google.com/github/gmn-data-platform/gmn-data-endpoints/blob/main/gmn_data_analysis_template_dev.ipynb\n.. _IAU: https://www.ta3.sk/IAUC22DB/MDC2007/\n.. _AVRO: https://avro.apache.org/docs/current/spec.html\n',
    'author': 'Ricky Bassom',
    'author_email': 'rickybas12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gmn-data-platform/gmn-python-api',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
