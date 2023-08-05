# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['isabelle_client']

package_data = \
{'': ['*'], 'isabelle_client': ['resources/*']}

extras_require = \
{':python_version < "3.7"': ['dataclasses'],
 ':python_version < "3.9"': ['importlib-resources']}

setup_kwargs = {
    'name': 'isabelle-client',
    'version': '0.3.6',
    'description': 'A client to Isabelle proof assistant server',
    'long_description': "|Binder|\\ |PyPI version|\\ |Anaconda version|\\ |CircleCI|\\ |Documentation Status|\\ |codecov|\n\nPython client for Isabelle server\n=================================\n\n``isabelle-client`` is a TCP client for\n`Isabelle <https://isabelle.in.tum.de>`__ server. For more information\nabout the server see part 4 of `the Isabelle system\nmanual <https://isabelle.in.tum.de/dist/Isabelle2021-1/doc/system.pdf>`__.\n\nHow to Install\n==============\n\nThe best way to install this package is to use ``pip``:\n\n.. code:: sh\n\n   pip install isabelle-client\n\n\nAnother option is to use Anaconda:\n\n.. code:: sh\n\t  \n   conda install -c conda-forge isabelle-client \n\nOne can also download and run the client together with Isabelle in a\nDocker contanier:\n\n.. code:: sh\n\n   docker build -t isabelle-client https://github.com/inpefess/isabelle-client.git\n   docker run -it --rm -p 8888:8888 isabelle-client jupyter-lab --ip=0.0.0.0 --port=8888\n\nHow to use\n==========\n\nFollow the `usage\nexample <https://isabelle-client.readthedocs.io/en/latest/usage-example.html#usage-example>`__\nfrom documentation, run the\n`script <https://github.com/inpefess/isabelle-client/blob/master/examples/example.py>`__,\nor use ``isabelle-client`` from a\n`notebook <https://github.com/inpefess/isabelle-client/blob/master/examples/example.ipynb>`__,\ne.g.\xa0with\n`Binder <https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=isabelle-client-examples/example.ipynb>`__ (Binder might fail with 'Failed to create temporary user for ...' error which is `well known <https://mybinder-sre.readthedocs.io/en/latest/incident-reports/2018-02-20-jupyterlab-announcement.html>`__ and related neither to ``isabelle-client`` nor to the provided ``Dockerfile``. If that happens, try to run Docker as described in the section above).\n\nHow to Contribute\n=================\n\n`Pull requests <https://github.com/inpefess/isabelle-client/pulls>`__\nare welcome. To start:\n\n.. code:: sh\n\n   git clone https://github.com/inpefess/isabelle-client\n   cd isabelle-client\n   # activate python virtual environment with Python 3.6+\n   pip install -U pip\n   pip install -U setuptools wheel poetry\n   poetry install\n   # recommended but not necessary\n   pre-commit install\n\nTo check the code quality before creating a pull request, one might run\nthe script\n`local-build.sh <https://github.com/inpefess/isabelle-client/blob/master/local-build.sh>`__.\nIt locally does nearly the same as the CI pipeline after the PR is\ncreated.\n\nReporting issues or problems with the software\n==============================================\n\nQuestions and bug reports are welcome on `the\ntracker <https://github.com/inpefess/isabelle-client/issues>`__.\n\nMore documentation\n==================\n\nMore documentation can be found\n`here <https://isabelle-client.readthedocs.io/en/latest>`__.\n\nVideo example\n=============\n\n.. image:: ../../examples/tty.gif\n  :alt:\n\n(if not displayed correctly on this page, please watch `here <https://isabelle-client.readthedocs.io/en/latest/#video-example>`__).\n\nHow to cite\n===========\n\nIf you’re writing a research paper, you can cite Isabelle client (and\nIsabelle 2021) using the `following\nDOI <https://doi.org/10.1007/978-3-030-81097-9_20>`__.\n\n.. |PyPI version| image:: https://badge.fury.io/py/isabelle-client.svg\n   :target: https://badge.fury.io/py/isabelle-client\n.. |Anaconda version| image:: https://anaconda.org/conda-forge/isabelle-client/badges/version.svg\n   :target: https://anaconda.org/conda-forge/isabelle-client\n.. |CircleCI| image:: https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg\n   :target: https://circleci.com/gh/inpefess/isabelle-client\n.. |Documentation Status| image:: https://readthedocs.org/projects/isabelle-client/badge/?version=latest\n   :target: https://isabelle-client.readthedocs.io/en/latest/?badge=latest\n.. |codecov| image:: https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/inpefess/isabelle-client\n.. |Binder| image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=isabelle-client-examples/example.ipynb\n\n",
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/isabelle-client',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
