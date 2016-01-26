# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
import transaction

from glottolog3.scripts.util import recreate_treeclosure, get_args


def main(args):  # pragma: no cover
    with transaction.manager:
        recreate_treeclosure()


if __name__ == '__main__':
    main(get_args())
