# -*- coding: utf-8 -*-
"""
The description status browser does not work on data from the database directly, instead
it works on data loaded from a json file. This file is created with this script.
"""
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

import glottolog3
from glottolog3.models import Languoid, LanguoidLevel, LanguoidStatus
from glottolog3.maps import COLOR_MAP


DOCTYPES = [
    'grammar',
    'grammarsketch',
    'dictionary',
    'specificfeature',
    'phonology',
    'text',
    'newtestament',
    'wordlist',
    'comparative',
    'minimal',
    'socling',
    'socling',
    'dialectology',
    'overview',
    'ethnographic',
    'bibliographical',
    'unknown']


class Source(object):
    """Representation of a source amenable to computation of MEDs
    (Most Extensive Description)
    """
    def __init__(self, source):
        self.index = len(DOCTYPES)
        self.doctype = None
        doctypes = (source.doctypes_str or '').split(', ')

        for doctype in doctypes:
            if doctype and DOCTYPES.index(doctype) < self.index:
                self.index = DOCTYPES.index(doctype)
                self.doctype = doctype

        # the number of pages is disvided by number of doctypes times number of
        # described languages
        self.pages = int(ceil(
            float(source.pages_int or 0) / (len(doctypes)*len(source.languages))))

        self.year = source.year_int
        self.id = source.id

    def __json__(self):
        return dict(doctype=self.doctype, year=self.year, pages=self.pages, id=self.id)

    def __cmp__(self, other):
        """This is the algorithm:
        "more extensive" means: better doctype (i.e. lower index) or more pages or newer.

        Thus, a sorted list of Sources will have the MED as first element.
        """
        return cmp(
            (self.index, -self.pages, -(self.year or 0), int(self.id)),
            (other.index, -other.pages, -(other.year or 0), int(other.id)))


def main(args):  # pragma: no cover
    icons_dir = path(glottolog3.__file__).dirname().joinpath('static', 'icons')
    for color, desc in COLOR_MAP.values():
        figure(figsize=(0.3, 0.3))
        axes([0.1, 0.1, 0.8, 0.8])
        coll = pie((100,), colors=('#' + color,))
        coll[0][0].set_linewidth(0.5)
        savefig(icons_dir.joinpath('c%s.png' % color), transparent=True)

    meds = {}
    start = time.time()
    with transaction.manager:
        # loop over active, established languages with geo-coords
        for i, l in enumerate(
            DBSession.query(Language)
            .options(joinedload(Languoid.macroareas))
            .filter(Language.active == True)
            .filter(Languoid.status == LanguoidStatus.established)
            .filter(Language.latitude != None)
            .filter(Languoid.level == LanguoidLevel.language)
        ):
            # let's collect the relevant sources in a way that allows computation of med.
            sources = sorted(map(Source, l.sources))

            # keep the overall med
            # note: this source may not be included in the potential meds computed below,
            # e.g. because it may not have a year.
            med = sources[0].__json__() if sources else None

            # now we have to compute meds respecting a cut-off year.
            # to do so, we collect eligible sources per year and then
            # take the med of this collection.
            potential_meds = []

            # we only have to loop over publication years within all sources, because
            # only in these years something better might have come along.
            for year in set(s.year for s in sources if s.year):
                # let's see if something better was published!
                eligible = [s for s in sources if s.year and s.year <= year]
                if eligible:
                    potential_meds.append(sorted(eligible)[0])

            meds[l.id] = {
                'id': l.id,
                'name': l.name,
                'latitude': l.latitude,
                'longitude': l.longitude,
                'macroareas': [ma.name for ma in l.macroareas],
                'med': med,
                'sources': [s.__json__() for s in
                            sorted(set(potential_meds), key=lambda s: -s.year)]}

            if i % 100 == 0:
                now = time.time()
                print i, '--', now - start
                start = now

    print len(meds), 'languages'

    with open('meds.json', 'w') as fp:
        json.dump(meds, fp)


if __name__ == '__main__':
    main(parsed_args())
