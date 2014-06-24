# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import transaction
from clld.scripts.util import parsed_args, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from glottolog3.models import Languoid


DATA_FILE = 'unesco_atlas_languages_limited_dataset.csv'
VITALITY_VALUES = [
    ('Vulnerable', 'most children speak the language, but it may be restricted to certain domains (e.g., home)'),
    ('Definitely endangered', 'children no longer learn the language as mother tongue in the home'),
    ('Severely endangered', 'language is spoken by grandparents and older generations; while the parent generation may understand it, they do not speak it to children or among themselves'),
    ('Critically endangered', 'the youngest speakers are grandparents and older, and they speak the language partially and infrequently'),
    ('Extinct', 'there are no speakers left'),
]


def main(args):
    data = Data()
    count = 0
    notfound = {}
    with transaction.manager:
        contrib = common.Contribution(
            id='unesco',
            name='Atlas of the World’s Languages in Danger',
            description='Atlas of the World’s Languages in Danger, © UNESCO, http://www.unesco.org/culture/languages-atlas')
        param = common.Parameter(
            id='vitality',
            name='Degree of endangerment')
        for i, spec in enumerate(VITALITY_VALUES):
            number = i + 1
            name, desc = spec
            data.add(
                common.DomainElement,
                name,
                id='vitality-%s' % number,
                name=name,
                description=desc,
                number=number,
                parameter=param)
        for item in reader(args.data_file(DATA_FILE), dicts=True):
            if item['ISO639-3 codes']:
                for code in item['ISO639-3 codes'].split(','):
                    code = code.strip()
                    lang = Languoid.get(code, key='hid', default=None)
                    if lang:
                        count += 1
                        item['url'] = 'http://www.unesco.org/culture/languages-atlas/en/atlasmap/language-iso-%s.html' % code
                        lang.update_jsondata(unesco=item)
                        de = data['DomainElement'][item['Degree of endangerment']]
                        vs = common.ValueSet(
                            id='vitality-%s' % lang.id,
                            name=de.name,
                            parameter=param,
                            contribution=contrib,
                            language=lang)
                        DBSession.add(common.Value(valueset=vs, name=de.name, domainelement=de))
                    else:
                        notfound[code] = 1
    print 'assigned', count, 'unesco urls'
    print 'missing iso codes:', notfound


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args((("--version",), dict(default=""))))