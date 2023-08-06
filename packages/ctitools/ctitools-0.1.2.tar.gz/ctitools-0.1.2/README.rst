Ctitools
========

Work with cti index files for the Heise papers c’t and iX

Description
-----------

This project provides diffrent tool for processing index files from
Heise papers c’t and iX.

Saving the current base dataset, downloaded from Heise and extractng to
data, the commdn

.. code:: shell

  > cti2bibtex data/inhalt.frm result.bibtex

creates a ``.bib`` file with 82100 entries. Importing this result in
Zotero took more than 28h and use more than 7GB of RAM.

Installation
------------

.. code:: shell

  > pip install git+https://gitlab.com/berhoel/python/ctitools.git

Usage
-----

usage:
  Read cti file. [-h] [--limit-year LIMIT_YEAR] [--limit-issue LIMIT_ISSUE] [--limit-journal LIMIT_JOURNAL] cti [bibtex]

positional arguments:
  cti                   input file

  bibtex                output file

options:
  -h, --help            show this help message and exit
  --limit-year LIMIT_YEAR
                        limit output to given year (default: all years in input file)
  --limit-issue LIMIT_ISSUE
                        limit output to given issue (dafault: all issues)
  --limit-journal LIMIT_JOURNAL
                        limit output to given magazine('i' for iX, or 'c' for c't) (default: all magazins)

Documentation
-------------

Documentation can be found `here <https://www.höllmanns.de/python/ctitools/>`_

Authors
-------

- Berthold Höllmann <berhoel@gmail.com> 

Project status
--------------

The projects works for converting the `cti` and `frm` file, provided by Heise, to `bib` files.
