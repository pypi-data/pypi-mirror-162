#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Test article entry processing.
"""

# Standard library imports.
from io import StringIO

# Third party library imports.
import pytest

# First party library imports.
from berhoel.ctitools import CTI

__date__ = "2022/08/06 17:31:45 Berthold Höllmann"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture
def cti_entry_1():
    return """Java nur mit -server-Option

Dr. Volker Zota, Dusan Wasserb╟╧ch
vza
154
10
c07


Praxis,Hotline,Java, Server, Internet, Programmierung, JAR-Archiv

Von Torsten T. Will und Ein Autor, Duzan Zivadinovic
ola
 74
 3
c08

kurz vorgestellt,Code Review, Open Source, Entwicklungssystem,Entwicklungs-Tools,Open-Source-Projekt Review Board
"""


@pytest.fixture
def cti_entry_2():
    return """Doppelt gemoppelt

Von Torsten T. Will und Ein Autor, Duzan Zivadinovic
ola
 74
 3
c08

kurz vorgestellt,Code Review, Open Source, Entwicklungssystem,Entwicklungs-Tools,Open-Source-Projekt Review Board
"""


def test_process_author_1(cti_entry_1):
    inp = StringIO(cti_entry_1)
    probe = CTI(inp)
    assert probe.entries.pop(0).author == ["Dr. Volker Zota", "Dušan Wasserbäch"]


def test_process_author_2(cti_entry_2):
    inp = StringIO(cti_entry_2)
    probe = CTI(inp)
    assert probe.entries.pop().author == [
        "Torsten T. Will",
        "Ein Autor",
        "Dušan Živadinović",
    ]


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%Y/%02m/%02d %02H:%02M:%02S %L\""
# End:
