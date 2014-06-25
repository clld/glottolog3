# -*- coding: utf-8 -*-
import transaction
from clld.scripts.util import parsed_args

from glottolog3.scripts.util import update_reflang


if __name__ == '__main__':  # pragma: no cover
    with transaction.manager:
        update_reflang(parsed_args((("--version",), dict(default=""))))
