# coding: utf8
from __future__ import unicode_literals, print_function
import io
from collections import OrderedDict
import re

import transaction
from clld.db.meta import DBSession
from clld.db.models.common import Source, LanguageSource
from clldutils.path import Path
from clldutils.misc import slug
from clldutils.inifile import INI

from glottolog3.scripts.util import get_args
from glottolog3.models import Languoid, LanguoidLevel


UNCL_COUNT = 10000


class UnclassifiedGroup(object):
    def __init__(self, name):
        global UNCL_COUNT
        UNCL_COUNT -= 1
        self.name = name
        self.level = LanguoidLevel.family
        self.id = 'un%s%s' % (slug(name)[:2], UNCL_COUNT)
        self.children = []
        self.jsondata = {}


def mkdir(lang, triggers, parent=None):
    # turn "Unclassified xxx" into an extra dir!
    if lang.jsondata.get('hname', '').startswith('Unclassified'):
        parent = mkdir(UnclassifiedGroup(lang.jsondata['hname']), triggers, parent=parent)

    parent = parent or Path('.')
    fname = '%s.%s' % (slug(lang.name), lang.id)
    d = parent.joinpath(fname)
    d.mkdir(exist_ok=True)

    subgroup = lang.level == LanguoidLevel.family
    md = INI(interpolation=None)
    for section, options in [
        ('core', [
            ('name', lang.name),
            ('glottocode', lang.id),
            ('hid', getattr(lang, 'hid', None)),
            ('level', lang.level.value),
            ('iso639-3', getattr(lang, 'iso_code', None)),
            ('latitude', getattr(lang, 'latitude', None)),
            ('longitude', getattr(lang, 'longitude', None)),
            ('macroareas', None if subgroup else [ma.name for ma in lang.macroareas]),
            ('countries', None if subgroup else ['%s (%s)' % (c.name, c.id) for c in lang.countries]),
            ('status', getattr(lang, 'endangerment', None)),
        ]),
        ('alternative names', [
            ('ethnologue', None),
            ('wals', None)
        ]),
        ('classification', [
            ('family', lang.fc.description if getattr(lang, 'fc', None) else None),
            ('sub', lang.sc.description if getattr(lang, 'sc', None) else None)
        ])
    ]:
        for option, value in options:
            md.set(section, option, value)

    if not isinstance(lang, UnclassifiedGroup):
        refs = []
        for ref in DBSession.query(Source).join(LanguageSource)\
                .filter(LanguageSource.language_pk == lang.pk):
            refs.append('%s (%s)' % (ref.name, ref.id))
        md.set('sources', 'glottolog', refs or None)

        altnames = OrderedDict()
        for provider in [
            'Glottolog',
            'WALS',
            'WALS other',
            'Harald Hammarström',
            'Ruhlen (1987)',
            'Moseley & Asher (1994)',
            'multitree',
            'lexvo',
        ]:
            altnames[provider] = set()

        for name in lang.get_identifier_objs('name'):
            if name.description == 'Glottolog' and name.name == lang.name:
                continue
            n = name.name
            if name.description == 'lexvo' and name.lang:
                n = '%s [%s]' % (n, name.lang)
            altnames[name.description].add(n)

        for prov, names in altnames.items():
            md.set('altnames', prov, sorted(list(names)) or None)

        _triggers = OrderedDict()
        for type_ in triggers:
            if lang.hid in triggers[type_]:
                _triggers[type_] = triggers[type_][lang.hid]
        for k, v in _triggers.items():
            md.set('triggers', k, v or None)

    md.write(d.joinpath('%s.ini' % fname).as_posix())

    for child in lang.children:
        mkdir(child, triggers, d)

    return d


def main(args):
    code_pattern = re.compile('{(?P<code>[^}]+)}$')
    triggers = OrderedDict()
    triggers['lgcode'] = {}
    triggers['inlg'] = {}

    for type_ in triggers:
        cfg = INI(interpolation=None)
        with io.open(args.data_dir.joinpath('references', 'alt4%s.ini' % type_), encoding='utf8') as fp:
            cfg.readfp(fp)
        for section in cfg.sections():
            match = code_pattern.search(section)
            if match:
                triggers[type_][match.group('code')] = cfg.get(section, 'triggers')

    roots = [
        row[0] for row in DBSession.query(Languoid.pk)
        .filter(Languoid.active == True)
        .filter(Languoid.father_pk == None)]

    for root in roots:
        root = DBSession.query(Languoid).filter(Languoid.pk == root).one()
        print(root.name)
        mkdir(root, triggers)
        transaction.abort()
        transaction.begin()


if __name__ == '__main__':
    main(get_args())
