from datetime import date

from sqlalchemy import or_, desc
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source

from glottolog3.models import (
    Languoid, LanguoidStatus, LanguoidLevel, Macroarea, Doctype, Refprovider, Provider,
)
from glottolog3.config import CFG


def glottologmeta(request):
    q = DBSession.query(Languoid)\
        .filter(Language.active == True)\
        .filter(or_(Languoid.status == LanguoidStatus.established,
                    Languoid.status == LanguoidStatus.unattested))
    qt = q.filter(Languoid.father_pk == None)
    res = {
        'last_update': DBSession.query(Language.updated)\
        .order_by(desc(Language.updated)).first()[0],
        'number_of_families': qt.filter(Languoid.level == LanguoidLevel.family).count(),
        'number_of_isolates': qt.filter(Languoid.level == LanguoidLevel.language).count(),
    }
    ql = q.filter(Languoid.hid != None)
    res['number_of_languages'] = {
        'all': ql.count(),
        'pidgin': qt.filter(Language.name == 'Pidgin').one().child_language_count,
        'artificial': qt.filter(Language.name == 'Artificial Language').one().child_language_count,
        'sign': sum(l.child_language_count for l in qt.filter(Language.name.contains('Sign '))),
    }
    res['number_of_languages']['l1'] = res['number_of_languages']['all'] \
        - res['number_of_languages']['pidgin']\
        - res['number_of_languages']['artificial']\
        - res['number_of_languages']['sign']
    return res


def credits(request):
    return {'stats': Refprovider.get_stats()}


def glossary(request):
    return {
        'macroareas': DBSession.query(Macroarea).order_by(Macroarea.id),
        'doctypes': DBSession.query(Doctype).order_by(Doctype.name)}


def cite(request):
    return {'date': date.today(), 'refs': CFG['PUBLICATIONS']}


def downloads(request):
    return {}


def errata(request):
    return {}


def contact(request):
    return {}


def families(request):
    return {'dt': request.get_datatable('languages', Language, type='families')}


def languages(request):
    return {'dt': request.get_datatable('languages', Language, type='languages')}


def get_filtered_params(request):
    res = dict(param_spec=[
        ('author', 'Author'),
        ('year', 'Precise year'),
        ('after', 'Start year'),
        ('before', 'End year'),
        ('title', 'Title'),
        ('editor', 'Editor'),
        ('journal', 'Journal'),
        ('address', 'Address'),
        ('publisher', 'Publisher'),
    ])
    res['params'] = {}
    for spec in res['param_spec']:
        res['params'][spec[0]] = request.params.get(spec[0], u'').strip()
    return res


def langdocquery(request):
    return get_filtered_params(request)


def langdoccomplexquery(request):
    res = get_filtered_params(request)

    #languoids, macroareas, reftypes
    if request.params.get('languoids'):
        res['params']['languoids'] = [
            m.group('code') for m in
            GLOTTOCODE_PATTERN.finditer(request.params['languoids'].replace('\n', ' '))]

    res['params']['macroareas'] = map(int, request.params.getall('macroarea'))
    res['params']['reftypes'] = map(int, request.params.getall('reftype'))
    res['params']['iso'] = request.params.getall('iso')
    res['refs'] = []#getRefs(**res['params'])

    fmt = request.params.get('format')
    if fmt == 'html':
        return render_to_response('reflist.mako', {'refs': res['refs'][1]}, request=request)
    if fmt == 'bib' or fmt == 'txt':
        if fmt == 'bib':
            c = '\n\n'.join(rec.bibtex().__unicode__().encode('utf8') for rec in res['refs'][1])
        else:
            c = '\n\n'.join(rec.txt().encode('utf8') for rec in res['refs'][1])
        return Response(c, content_type='text/plain; charset=UTF-8')

    res.update(
        reftypes=DBSession.query(Doctype).order_by(Doctype.id),
        macroareas=DBSession.query(Macroarea).order_by(Macroarea.id))
    return res
