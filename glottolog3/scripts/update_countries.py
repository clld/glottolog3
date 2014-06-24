# -*- coding: utf-8 -*-
"""
Updating the language-country relationships
-------------------------------------------

We only add new relationships for languages which so far have not been related to any
country. This is to make sure the relationships determined by algorithms other than
Harald's remain stable.
"""
import transaction
from clld.scripts.util import parsed_args
from clld.lib import dsv

from glottolog3.models import Languoid, Country


def main(args):
    count = 0
    countries = {}
    languages = {}
    with transaction.manager:
        for row in dsv.reader(
                args.data_file(args.version, 'countries.tab'), encoding='latin1'):
            hid, cnames = row[0], row[1:]
            if hid not in languages:
                languages[hid] = Languoid.get(hid, key='hid', default=None)
            if not languages[hid]:
                continue
            l = languages[hid]
            if l.countries:
                continue
            for cname in set(cnames):
                if cname not in countries:
                    countries[cname] = Country.get(cname, key='name', default=None)
                if not countries[cname]:
                    continue
                c = countries[cname]
                if c.id not in [_c.id for _c in l.countries]:
                    l.countries.append(c)
                    count += 1

    print count, 'relations added'


if __name__ == '__main__':  # pragma: no cover
    with transaction.manager:
        main(parsed_args((("--version",), dict(default="2.0"))))