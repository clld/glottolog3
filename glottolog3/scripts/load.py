# -*- coding: utf-8 -*-
import os
from functools import partial
import json

import transaction
from clld.scripts.util import parsed_args, data_file


if __name__ == '__main__':  # pragma: no cover
    add_args = [
        (("version",), dict(help="X.Y")),
        (("what",), dict()),
        (("command",), dict(help="download|verify|update")),
        (("--api-key",), dict(default=os.environ.get('GBS_API_KEY'))),
    ]

    args = parsed_args(*add_args)
    assert args.data_file(args.version).exists()
    args.data_file = partial(data_file, args.module, args.version, args.what)
    if not args.data_file().exists():
        args.data_file().mkdir()

    mod = __import__(
        'glottolog3.scripts.loader.' + args.what, fromlist=[args.command, 'JSON'])
    args.json = None
    if getattr(mod, 'JSON', None) and args.data_file(mod.JSON).exists():
        with open(args.data_file(mod.JSON)) as fp:
            args.json = json.load(fp)

    with transaction.manager:
        res = getattr(mod, args.command)(args)
    if res is not None and args.command == 'download' and getattr(mod, 'JSON', None):
        with open(args.data_file(mod.JSON), 'w') as fp:
            json.dump(res, fp)
