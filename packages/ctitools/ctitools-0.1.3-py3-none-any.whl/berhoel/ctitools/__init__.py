#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Work with cti index files for the Heise papers c't and iX
"""

# Standard library imports.
import re
import argparse

# Local library imports.
from .ct import Ct
from .ix import Ix

__date__ = "2022/08/06 17:36:01 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"

try:
    # Local library imports.
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0.invalid0"


class CTI:
    """Read entries from cti files:

    .. code:: asc

      Bürokratie: Mit analoger Wucht

      Tim Gerber
      tig
        3
      16
      c22

      Standpunkt,Immer in c't,Gesellschaft,Ukraine-Krieg,Ukraine-Hilfe,Digitalisierung,eGovernment,Ukraine-Flüchtlinge
    """

    paper_year = re.compile(r"(?P<paper>[ci])(?P<year>[0-9]{2})")
    paper_map = {"i": "iX", "c": "c't magazin für computertechnik"}

    wrong_char_coding_auml_re = re.compile("|".join(("╟╧",)))

    def __init__(self, infile, limit_year=None, limit_issue=None, limit_journal=None):
        """Read input file.

        Args:
          infile (file): Input file
          limit_year (int): Limit output to given year
          limit_issue (int): Limit output to given issue
          limit_journal (str): Limit output to given journal
        """
        self.entries = []
        for shorttitle in infile:
            shorttitle = self.fix_chars(shorttitle)
            title = self.fix_chars(next(infile))
            author = self.fix_author(self.fix_chars(next(infile)))
            next(infile)  # author shortsign
            pages = int(next(infile).strip())
            issue = int(next(infile).strip())
            info = self.paper_year.match(next(infile).strip()).groupdict()
            journal = info["paper"]
            year = int(info["year"])
            year += 1900 if year > 80 else 2000
            references = next(infile).strip()
            keywords = self.fix_chars(next(infile))
            if (
                (limit_issue is not None and issue != limit_issue)
                or (limit_journal is not None and journal != limit_journal)
                or (limit_year is not None and year != limit_year)
            ):
                continue
            self.entries.append(
                {"c": Ct, "i": Ix}[journal](
                    shorttitle=shorttitle,
                    title=title,
                    author=author,
                    pages=pages,
                    issue=issue,
                    info=info,
                    year=year,
                    references=references,
                    keywords=keywords,
                )()
            )

    @staticmethod
    def fix_chars(inp):
        return "ä".join(CTI.wrong_char_coding_auml_re.split(inp)).strip()

    dusan_replace_re = re.compile(
        "|".join(
            (
                "Duzan",
                "Dusan",
            )
        )
    )
    zivadinovic_replace_re = re.compile(
        "|".join(
            (
                "Zivadinovic",
                "Zivadinovi∩c",
                "Zivadinovi'c",
                "Zivadanovic",
                "Zivadinivic",
            )
        )
    )

    @staticmethod
    def fix_author(author):
        """Fix author infoprmation

        Args:
          author (str):

        Returns:
          str
        """
        author = author.replace(" und ", ", ")
        author = author.replace("Von ", "")
        author = "Dušan".join(CTI.dusan_replace_re.split(author))
        author = "Živadinović".join(CTI.zivadinovic_replace_re.split(author))

        return [i.strip() for i in author.split(",")]


def main():
    parser = argparse.ArgumentParser("Read cti file.")
    args = parser.parse_args()

    CTI(args.cti)


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
