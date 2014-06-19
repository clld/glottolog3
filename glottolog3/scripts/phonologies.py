import json

from sqlalchemy import not_
from sqlalchemy.orm import joinedload

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession

from glottolog3.models import Ref, Doctype, Languoid, Provider


def main(args):
    with open(args.data_file('phoible-isocodes.json')) as fp:
        covered = json.load(fp).keys()

    q = DBSession.query(Ref).join(Ref.languages).join(Ref.doctypes).join(Ref.providers)\
        .filter(Doctype.pk.in_([3, 8, 11]))\
        .filter(Provider.pk == 21)\
        .filter(not_(Languoid.hid.in_(covered)))\
        .options(joinedload(Ref.languages))
    print q.count()

    with open(args.data_file('phoible-phonologies.bib'), 'w') as fp:
        for ref in q:
            rec = ref.bibtex()
            rec['glottolog_url'] = 'http://glottolog.org/resource/reference/id/%s' % ref.id
            rec['languages'] = ', '.join('%s [%s][%s]' % (l.name, l.id, l.hid) for l in ref.languages if l.hid not in covered)
            fp.write('\n%s' % unicode(rec).encode('utf8'))


if __name__ == '__main__':
    main(parsed_args())
