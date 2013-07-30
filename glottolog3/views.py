from datetime import date
import re

import colander
from purl import URL
from sqlalchemy import or_, desc
from sqlalchemy.sql.expression import func
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageSource
from clld.db.util import icontains

from glottolog3.models import (
    Languoid, LanguoidStatus, LanguoidLevel, Macroarea, Doctype, Refprovider, Provider,
    TreeClosureTable, Ref, Refmacroarea, Refdoctype,
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


def childnodes(request):
    if request.params.get('t') == 'select2':
        query = DBSession.query(Languoid.id, Languoid.name, Languoid.level)\
            .filter(icontains(Languoid.name, request.params.get('q')))
        total = query.count()
        return dict(
            results=[{
                'text': '%s (%s)' % (l.name, l.id),
                'id': l.id,
                'level': l.level.value} for l in query.limit(100)],
            context={},
            more=total > 500)

    query = DBSession.query(
        Languoid.pk,
        Languoid.id,
        Languoid.name,
        Languoid.level,
        func.count(TreeClosureTable.child_pk).label('children'))\
        .filter(Language.pk == TreeClosureTable.parent_pk)\
        .filter(Language.active == True)

    if request.params.get('node'):
        query = query.filter(Languoid.father_pk == int(request.params['node']))
    else:
        # narrow down selection of top-level nodes in the tree:
        query = query.filter(Languoid.father_pk == None)
        if request.params.get('q'):
            query = query.filter(Language.name.contains(request.params.get('q')))

    query = query.group_by(Languoid.pk,
        Languoid.id,
        Languoid.name,
        Languoid.level).order_by(Language.name)
    return [{
        'label': ('%s (%s)' % (l.name, l.children - 1))
            if l.children > 1 else l.name,
        'glottocode': l.id,
        'lname': l.name,
        'id': l.pk,
        'level': l.level.value,
        #'children': l.children
        'load_on_demand': l.children > 1} for l in query]


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


def langdocquery(request):
    return get_filtered_params(request)


YEAR_PATTERN = re.compile('[0-9]{4}$')


from glottolog3.util import getRefs, get_params
from glottolog3.datatables import Refs


def langdoccomplexquery(request):
    res = {
        'dt': None,
        'doctypes': DBSession.query(Doctype).order_by(Doctype.id),
        'macroareas': DBSession.query(Macroarea).order_by(Macroarea.id),
    }
    res['params'], reqparams = get_params(request.params, **res)
    res['refs'] = getRefs(res['params'])

    #
    # TODO: initialize datatable with dict of query params for this query!
    #
    if res['refs']:
        res['dt'] = Refs(request, Source, cq=1, **reqparams)
        #URL(request.url).query_params()

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
        doctypes=DBSession.query(Doctype).order_by(Doctype.id),
        macroareas=DBSession.query(Macroarea).order_by(Macroarea.id))
    return res
