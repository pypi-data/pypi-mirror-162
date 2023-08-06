#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for cti (c't iX) entries.
"""

# Standard library imports.
from dataclasses import dataclass

__date__ = "2022/08/01 16:12:36 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@dataclass
class CTIEntry:
    """Store information from input file."""

    shorttitle: str
    title: str
    author: str
    pages: int
    issue: int
    info: str
    journaltitle: str
    date: str
    references: str
    keywords: str


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
