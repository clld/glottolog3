# -*- coding: utf-8 -*-
import transaction

from glottolog3.scripts.util import update_reflang, get_args


if __name__ == '__main__':  # pragma: no cover
    with transaction.manager:
        update_reflang(get_args())
