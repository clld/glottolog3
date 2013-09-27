# -*- coding: utf-8 -*-
import sys
import transaction
import re

from clld.scripts.util import parsed_args
from clld.lib import dsv
from clld.db.meta import DBSession
from clld.db.models.common import (
    Parameter, ValueSet, ValueSetReference, Value, Contribution, Source,
)

from glottolog3.models import Languoid
from glottolog3.lib.util import get_map, REF_PATTERN, PAGES_PATTERN
from glottolog3.lib.bibtex import unescape


WORD_PATTERN = re.compile('[a-z]+')


def main(args):  # pragma: no cover
    """
    - text goes into ValueSet.description
    - refs go into ValueSetReference objects
    """
    def normalized_pages(s):
        match = PAGES_PATTERN.match(s or '')
        if match:
            return match.group('pages')

    #
    # - create map from hname to active languoid
    #
    langs_by_hid = {}
    langs_by_hname = {}
    langs_by_name = {}
    with transaction.manager:
        for l in DBSession.query(Languoid).filter(Languoid.active == False):
            langs_by_hname[l.jsondatadict.get('hname')] = l
            langs_by_hid[l.hid] = l
            langs_by_name[l.name] = l

        for l in DBSession.query(Languoid).filter(Languoid.active == True):
            langs_by_hname[l.jsondatadict.get('hname')] = l
            langs_by_hid[l.hid] = l
            langs_by_name[l.name] = l

        for id_, type_ in [('fc', 'family'), ('sc', 'subclassification')]:
            for i, row in enumerate(dsv.rows(args.data_file(args.version, '%s_justifications.tab' % type_))):
                name = row[0].decode('utf8')
                name = name.replace('_', ' ') if not name.startswith('NOCODE') else name
                l = langs_by_hname.get(name, langs_by_hid.get(name, langs_by_name.get(name)))
                if not l:
                    raise ValueError(name)

                _r = 3 if type_ == 'family' else 2
                comment = (row[_r].decode('utf8').strip() or None) if len(row) > _r else None
                if comment and not WORD_PATTERN.search(comment):
                    comment = None

                #
                # TODO: look for [NOCODE_ppp] patterns as well!?
                #

                refs = [(int(m.group('id')), normalized_pages(m.group('comment')))
                        for m in REF_PATTERN.finditer(row[2])]

                vs = None
                for _vs in l.valuesets:
                    if _vs.parameter.id == id_:
                        vs = _vs
                        break

                if not vs:
                    print l.id, type_, '++'
                    vs = ValueSet(
                        id='%s%s' % (type_, l.id),
                        description=comment,
                        language=l,
                        parameter=Parameter.get(id_),
                        contribution=Contribution.first())
                    DBSession.add(Value(
                        id='%s%s' % (type_, l.id),
                        name='%s - %s' % (l.level, l.status),
                        valueset=vs))
                    DBSession.flush()
                else:
                    if vs.description != comment:
                        print l.id, type_, '~~ description'
                        print vs.description
                        print comment
                        vs.description = comment

                for r in vs.references:
                    DBSession.delete(r)

                for r, pages in refs:
                        vs.references.append(ValueSetReference(
                            source=Source.get(str(r)),
                            description=pages))

            print i, type_


if __name__ == '__main__':
    main(parsed_args((("--version",), dict(default=""))))
