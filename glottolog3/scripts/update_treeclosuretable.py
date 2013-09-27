# -*- coding: utf-8 -*-
import sys

from clld.scripts.util import parsed_args

from glottolog3.scripts.util import recreate_treeclosure


def main(args):  # pragma: no cover
    recreate_treeclosure()


if __name__ == '__main__':
    main(parsed_args())
