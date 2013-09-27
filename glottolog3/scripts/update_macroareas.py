# -*- coding: utf-8 -*-
import transaction
from clld.scripts.util import parsed_args

from glottolog3.scripts.util import update_macroareas


if __name__ == '__main__':  # pragma: no cover
    with transaction.manager:
        update_macroareas(parsed_args((("--version",), dict(default="2.0"))))
