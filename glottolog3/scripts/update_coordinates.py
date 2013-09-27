# -*- coding: utf-8 -*-
import transaction
from clld.scripts.util import parsed_args

from glottolog3.scripts.util import update_coordinates


if __name__ == '__main__':  # pragma: no cover
    with transaction.manager:
        update_coordinates(parsed_args((("--version",), dict(default="2.0"))))
