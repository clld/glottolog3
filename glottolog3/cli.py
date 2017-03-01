# coding: utf8
from __future__ import unicode_literals, print_function, division
import sys

from clldutils.clilib import ArgumentParser
from clldutils.path import Path
from clld.scripts.util import setup_session
from pyglottolog.api import Glottolog

import glottolog3
from glottolog3 import commands
assert commands


def main():  # pragma: no cover
    setup_session('development.ini')
    parser = ArgumentParser('glottolog3')
    parser.add_argument(
        '--repos',
        help="path to glottolog data repository",
        type=Glottolog,
        default=Glottolog(
            Path(glottolog3.__file__).parent.parent.parent.joinpath('glottolog')))
    sys.exit(parser.main())
