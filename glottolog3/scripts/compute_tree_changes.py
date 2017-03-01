"""
"""
from __future__ import unicode_literals, print_function
from collections import Counter

from sqlalchemy.sql import select

from clld.db.meta import DBSession
from clld.db.models.common import Language

from pyglottolog.api import Glottolog

from glottolog3.models import Languoid
from glottolog3.scripts.util import get_args


def main(args):
    stats = Counter(new=0, matches=0, migrations=0, nomatches=0)

    # The new classification in clld/glottolog:
    repos = Glottolog(repos=args.data_dir)
    langs_repos = {l.id: l for l in repos.languoids()}
    codes_repos = set(langs_repos.keys())
    assert langs_repos

    l, ll = Language.__table__.alias('l'), Languoid.__table__.alias('ll')
    langs_db = {r['l_id']: r for r in DBSession.execute(
        select([l, ll], use_labels=True).where(l.c.pk == ll.c.pk)).fetchall()}
    langs_db_pk2id = {v['l_pk']: k for k, v in langs_db.items()}
    codes_db = set(langs_db.keys())

    def ancestors(db_lang):
        while db_lang['ll_father_pk'] in langs_db_pk2id:
            yield langs_db_pk2id[db_lang['ll_father_pk']]
            db_lang = langs_db[langs_db_pk2id[db_lang['ll_father_pk']]]

    for code in codes_repos.difference(codes_db):
        stats.update(['new'])
        print('+++ {0} - {1}'.format(code, langs_repos[code].level))

    for code in codes_db.difference(codes_repos):
        if langs_db[code]['l_active']:
            # In-active languoids will not be touched anyway, obsolete families will be
            # marked in-active.
            # Note: Do we want to relate obsolete families with their closest counterpart?
            # -> just compute closest sub-group above, which is still present!
            for i, ancestor in enumerate(ancestors(langs_db[code])):
                if ancestor in codes_repos:
                    print('{0} --> {1} {2}'.format(code, ancestor, i))
                    break
            else:
                print('== no replacement == {0}'.format(code))

        if langs_db[code]['l_active'] and '%s' % langs_db[code]['ll_level'] == 'language':
            stats.update(['obsolete'])
            print('--- {0} {1} - {2} {3} {4}'.format(code, langs_db[code]['l_name'], langs_db[code]['l_active'], langs_db[code]['ll_status'], langs_db[code]['ll_level']))

    for code in codes_db.intersection(codes_repos):
        stats.update(['match'])
        lang_db = langs_db[code]
        lang_repos = langs_repos[code]

        for key in [
            'l_longitude',
            'l_latitude',
            #'l_name',
            'll_hid',
            # TODO: iso code, level
        ]:
            attr = key.split('_', 1)[1]
            if lang_db[key] != getattr(lang_repos, attr):
                print('{0} {1}: {2} --> {3}'.format(code, attr, lang_db[key], getattr(lang_repos, attr)))

    print(stats)
    return


if __name__ == '__main__':
    main(get_args())
