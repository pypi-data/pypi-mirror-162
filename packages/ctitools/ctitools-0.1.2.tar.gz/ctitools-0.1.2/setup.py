# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['berhoel',
 'berhoel.ctitools',
 'berhoel.ctitools.cti2bibtex',
 'berhoel.ctitools.cti2bibtex.tests',
 'berhoel.ctitools.tests']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cti2bibtex = berhoel.ctitools.cti2bibtex:main']}

setup_kwargs = {
    'name': 'ctitools',
    'version': '0.1.2',
    'description': "Work with cti index files for the Heise papers c't and iX",
    'long_description': "Ctitools\n========\n\nWork with cti index files for the Heise papers c’t and iX\n\nDescription\n-----------\n\nThis project provides diffrent tool for processing index files from\nHeise papers c’t and iX.\n\nSaving the current base dataset, downloaded from Heise and extractng to\ndata, the commdn\n\n.. code:: shell\n\n  > cti2bibtex data/inhalt.frm result.bibtex\n\ncreates a ``.bib`` file with 82100 entries. Importing this result in\nZotero took more than 28h and use more than 7GB of RAM.\n\nInstallation\n------------\n\n.. code:: shell\n\n  > pip install git+https://gitlab.com/berhoel/python/ctitools.git\n\nUsage\n-----\n\nusage:\n  Read cti file. [-h] [--limit-year LIMIT_YEAR] [--limit-issue LIMIT_ISSUE] [--limit-journal LIMIT_JOURNAL] cti [bibtex]\n\npositional arguments:\n  cti                   input file\n\n  bibtex                output file\n\noptions:\n  -h, --help            show this help message and exit\n  --limit-year LIMIT_YEAR\n                        limit output to given year (default: all years in input file)\n  --limit-issue LIMIT_ISSUE\n                        limit output to given issue (dafault: all issues)\n  --limit-journal LIMIT_JOURNAL\n                        limit output to given magazine('i' for iX, or 'c' for c't) (default: all magazins)\n\nDocumentation\n-------------\n\nDocumentation can be found `here <https://www.höllmanns.de/python/ctitools/>`_\n\nAuthors\n-------\n\n- Berthold Höllmann <berhoel@gmail.com> \n\nProject status\n--------------\n\nThe projects works for converting the `cti` and `frm` file, provided by Heise, to `bib` files.\n",
    'author': 'Berthold Höllmann',
    'author_email': 'berthold@xn--hllmanns-n4a.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://python.xn--hllmanns-n4a.de/ctitools/',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
