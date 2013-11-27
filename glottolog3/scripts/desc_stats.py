# -*- coding: utf-8 -*-
import sys
import transaction
import json
from math import ceil
import time

from sqlalchemy.orm import joinedload
from path import path
from pylab import figure, axes, pie, savefig

from clld.scripts.util import parsed_args
from clld.db.models.common import Language
from clld.db.meta import DBSession
from clld.util import EnumSymbol

import glottolog3
from glottolog3.models import (
    Languoid, Macroarea, Superseded, LanguoidLevel, LanguoidStatus,
)


order = ['grammar', 'grammarsketch', 'dictionary', 'specificfeature', 'phonology', 'text', 'newtestament', 'wordlist', 'comparative', 'minimal', 'socling', 'socling', 'dialectology', 'overview', 'ethnographic', 'bibliographical', 'unknown']

htmlc = {}
htmlc['green'] = "00ff00"
htmlc['orange'] = "ff8040"
htmlc['orange red'] = "ff4500"
htmlc['red'] = "ff0000"
htmlc['light gray'] = "d3d3d3"
htmlc['slate gray'] = "708a90"
htmlc['black'] = "000000"
htmlc['dark green'] = "006400"


def main(args):  # pragma: no cover
    icons_dir = path(glottolog3.__file__).dirname().joinpath('static', 'icons')
    for color in htmlc.values():
        figure(figsize=(0.3, 0.3))
        axes([0.1, 0.1, 0.8, 0.8])
        coll = pie((100,), colors=('#' + color,))
        coll[0][0].set_linewidth(0.5)
        savefig(icons_dir.joinpath('c%s.png' % color), transparent=True)

    meds = {}
    s = time.time()
    with transaction.manager:
        for i, l in enumerate(
            DBSession.query(Language)
            .options(joinedload(Languoid.macroareas))
            .filter(Language.active == True)
            .filter(Language.latitude != None)
            .filter(Languoid.level == LanguoidLevel.language)
        ):
            sources = []
            for source in l.sources:
                index = len(order)
                doctype = 'unknown'
                doctypes = (source.doctypes_str or '').split(', ')

                for hhtype in doctypes:
                    if hhtype and order.index(hhtype) < index:
                        index = order.index(hhtype)
                        doctype = hhtype

                sources.append((
                    index,
                    int(ceil(float(source.pages_int or 0) / (len(doctypes)*len(source.languages)))),
                    doctype,
                    source.year_int,
                    source.id,
                    source.bibtex().text()))

            sources = sorted(sources, key=lambda t: (t[0], -t[1]))
            #
            # we only keep sources which may become MED for a certain cut-off year, i.e.
            # we remove those which are newer than the next better one.
            #
            cleaned_sources = sources[:1]
            if sources:
                year = sources[0][3] or 3000
                for source in sources[1:]:
                    if source[3] and source[3] < year:
                        cleaned_sources.append(source)
                        year = source[3]
            meds[l.id] = {
                'id': l.id,
                'name': l.name,
                'latitude': l.latitude,
                'longitude': l.longitude,
                'macroareas': [ma.name for ma in l.macroareas],
                'sources': [[t[2], t[1], t[3], t[4], t[5]] for t in cleaned_sources]}

            if i % 100 == 0:
                print i, '--', time.time() - s

    print len(meds), 'languages'

    with open('meds.json', 'w') as fp:
        json.dump(meds, fp)


if __name__ == '__main__':
    main(parsed_args())
