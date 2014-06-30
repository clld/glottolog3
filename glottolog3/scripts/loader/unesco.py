# -*- coding: utf-8 -*-
"""
Limited dataset downloaded in XLS from
http://www.unesco.org/culture/languages-atlas/index.php
and exported to csv from LibreOffice
"""
from __future__ import unicode_literals

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


def download(args):
    # because download requires a valid session, we simply copy from the previous version!
    for d in args.data_file('..', '..').dirs():
        s = d.joinpath('unesco', DATA_FILE)
        if s.exists() and str(s.abspath()) != str(args.data_file(DATA_FILE).abspath()):
            s.copy(args.data_file(DATA_FILE))


def update(args):
    pid, cid = 'vitality', 'unesco'
    count = 0
    notfound = {}
    contrib = common.Contribution.get(cid, default=None)
    if not contrib:
        contrib = common.Contribution(
            id=cid,
            name='Atlas of the World’s Languages in Danger',
            description='Atlas of the World’s Languages in Danger, © UNESCO, http://www.unesco.org/culture/languages-atlas')
    param = common.Parameter.get(pid, default=None)
    if param is None:
        param = common.Parameter(
            id=pid,
            name='Degree of endangerment')
    domain = {de.name: de for de in param.domain}
    for i, spec in enumerate(VITALITY_VALUES):
        name, desc = spec
        if name not in domain:
            number = i + 1
            domain[name] = common.DomainElement(
                id='%s-%s' % (pid, number),
                name=name,
                description=desc,
                number=number,
                parameter=param)
    valuesets = {vs.id: vs for vs in param.valuesets}
    for item in reader(args.data_file(DATA_FILE), dicts=True):
        if item['ISO639-3 codes']:
            for code in item['ISO639-3 codes'].split(','):
                code = code.strip()
                lang = Languoid.get(code, key='hid', default=None)
                if lang:
                    count += 1
                    item['url'] = 'http://www.unesco.org/culture/languages-atlas/en/atlasmap/language-iso-%s.html' % code
                    lang.update_jsondata(unesco=item)
                    de = domain[item['Degree of endangerment']]
                    vsid = '%s-%s' % (pid, lang.id)
                    vs = valuesets.get(vsid)
                    if not vs:
                        vs = common.ValueSet(
                            id='vitality-%s' % lang.id,
                            parameter=param,
                            contribution=contrib,
                            language=lang)
                        DBSession.add(common.Value(valueset=vs, name=de.name, domainelement=de))
                        valuesets[vsid] = vs
                    else:
                        vs.values[0].domainelement = de
                else:
                    notfound[code] = 1
    print 'assigned', count, 'unesco urls'
    print 'missing iso codes:', notfound
