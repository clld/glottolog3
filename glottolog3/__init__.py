from functools import partial

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.config import Configurator
from pyramid.response import Response
from sqlalchemy.orm import joinedload
from clld.interfaces import ICtxFactoryQuery, IDownload, IMapMarker, IDomainElement, IValueSet
from clld.web.app import menu_item, CtxFactoryQuery
from clld.web.icon import MapMarker
from clld.web.adapters.base import adapter_factory, Index
from clld.web.adapters.download import N3Dump, Download
from clld.db.models.common import Language, Source, ValueSet, ValueSetReference
from clldutils import svg

from glottolog3 import views
from glottolog3 import models
from glottolog3 import adapters
from glottolog3.interfaces import IProvider
from glottolog3.datatables import Providers


class GlottologMapMarker(MapMarker):
    def __call__(self, ctx, req):
        if IValueSet.providedBy(ctx):
            if ctx.values and ctx.values[0].domainelement:
                if 'icon' in ctx.values[0].domainelement.jsondatadict:
                    return svg.data_url(svg.icon(ctx.values[0].domainelement.jsondata['icon']))
        if IDomainElement.providedBy(ctx):
            if 'icon' in ctx.jsondatadict:
                return svg.data_url(svg.icon(ctx.jsondata['icon']))
        return super(GlottologMapMarker, self).__call__(ctx, req)


class GLCtxFactoryQuery(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        if model == Language:
            query = query.options(
                joinedload(models.Languoid.family),
                joinedload(models.Languoid.children),
                joinedload(Language.valuesets)
                    .joinedload(ValueSet.references)
                    .joinedload(ValueSetReference.source),
                joinedload(Language.valuesets).joinedload(ValueSet.values),
                joinedload(Language.valuesets).joinedload(ValueSet.parameter),
            )
        return query

    def __call__(self, model, req):
        if model == Language:
            # responses for no longer supported legacy codes
            if not models.Languoid.get(req.matchdict['id'], default=None):
                legacy = models.LegacyCode.get(req.matchdict['id'], default=None)
                if legacy:
                    raise HTTPMovedPermanently(location=legacy.url(req))
                # Fall through to `clld.web.app.ctx_factory` handling dealt out but no longer
                # active glottocodes by looking up `Config`.
        elif model == Source:
            if ':' in req.matchdict['id']:
                # We support Source URLs using the "qualified" bibtex key as ID.
                ref = req.db.query(models.Source)\
                    .join(models.Refprovider)\
                    .filter(models.Refprovider.id == req.matchdict['id'])\
                    .first()
                if ref:
                    raise HTTPMovedPermanently(location=req.route_url('source', id=ref.id))
        return super(GLCtxFactoryQuery, self).__call__(model, req)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['navbar.inverse'] = True
    settings['route_patterns'] = {
        'languages': '/glottolog/language',
        'language': '/resource/languoid/id/{id:[^/\.]+}',
        'source': '/resource/reference/id/{id:[^/\.]+}',
        'sources': '/langdoc',
        #'provider': '/langdoc/langdocinformation#provider-{id}',
        'providers': '/langdoc/langdocinformation',
    }
    settings['sitemaps'] = ['language', 'source']
    config = Configurator(settings=settings)
    #
    # Note: The following routes must be registered before including the clld web app,
    # because they are special cases of a more general route pattern registered there.
    #
    config.add_route('languoid.xhtml', '/resource/languoid/id/{id:[^/\.]+}.xhtml')
    config.add_route('reference.xhtml', '/resource/reference/id/{id:[^/\.]+}.xhtml')
    config.include('clldmpg')
    config.add_route_and_view(
        'robots',
        '/robots.txt',
        lambda req: Response(
            """Sitemap: {0}
User-agent: Linespider
Disallow: /
User-agent: SemrushBot
Disallow: /
User-agent: NaverBot
Disallow: /
User-agent: *
Disallow: /files/
""".format(req.route_url('sitemapindex')),
            content_type='text/plain'))
    config.registry.registerUtility(GlottologMapMarker(), IMapMarker)
    config.registry.registerUtility(GLCtxFactoryQuery(), ICtxFactoryQuery)
    config.register_menu(
        #('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages', label='Languages')),
        ('families', partial(menu_item, 'glottolog.families', label='Families')),
        ('search', partial(menu_item, 'glottolog.languages', label='Language Search')),
        ('sources', partial(menu_item, 'sources', label='References')),
        ('query', partial(menu_item, 'langdoc.complexquery', label='Reference Search')),
        ('about', partial(menu_item, 'about', label='About')),
    )
    config.register_resource('provider', models.Provider, IProvider, with_index=True)
    config.register_adapter(
        adapter_factory('provider/index_html.mako', base=Index), IProvider)
    config.add_view(views.redirect_languoid_xhtml, route_name='languoid.xhtml')
    config.add_view(views.redirect_reference_xhtml, route_name='reference.xhtml')

    config.add_route('macroareas_geojson', '/macroareas.geojson')
    config.add_view(views.macroareas_geojson, route_name='macroareas_geojson', renderer='json')

    config.add_route_and_view('news', '/news', views.news, renderer='news.mako')
    config.add_route_and_view(
        'glottolog.meta',
        '/glottolog/glottologinformation',
        views.glottologmeta,
        renderer='glottologmeta.mako')
    config.add_route_and_view(
        'glottolog.families',
        '/glottolog/family',
        views.families,
        renderer='families.mako')
    config.add_route_and_view(
        'glottolog.iso',
        '/resource/languoid/iso/{id:[^/\.]+}',
        views.iso)
    config.add_route_and_view(
        'glottolog.languages',
        '/glottolog',
        views.languages,
        renderer='language/search_html.mako')
    config.add_route_and_view(
        'glottolog.childnodes',
        '/db/getchildlects',
        views.childnodes,
        renderer='json')
    config.add_route_and_view(
        'langdoc.complexquery',
        '/langdoc/complexquery',
        views.langdoccomplexquery,
        renderer='langdoccomplexquery.mako')

    for name in 'credits glossary cite downloads contact'.split():
        pp = '/' if name == 'credits' else '/meta/'
        config.add_route_and_view(
            'home.' + name,
            pp + name,
            getattr(views, name),
            renderer=name + '.mako')

    assert config.registry.unregisterUtility(provided=IDownload, name='dataset.cldf')
    config.register_download(adapters.LanguoidCsvDump(
        models.Languoid, 'glottolog3', description="Languoids as CSV"))
    config.register_download(adapters.LanguoidTurtleDump(
        Language, 'glottolog3', description="Languoids as RDF"))
    config.register_download(adapters.LanguoidN3Dump(
        Language, 'glottolog3', description="Languoids as RDF"))
    config.register_download(Download(
        Source, 'glottolog3', ext='bib', description="References as BibTeX"))
    config.register_download(N3Dump(
        Source, 'glottolog3', description="References as RDF"))

    config.add_route('langdocstatus', '/langdoc/status')
    config.add_route('langdocstatus.browser', '/langdoc/status/browser')
    config.add_route(
        'langdocstatus.languages', '/langdoc/status/languages-{ed:[0-9]}-{sdt:[0-9]}')
    config.scan('glottolog3.langdocstatus')
    config.register_datatable('providers', Providers)
    return config.make_wsgi_app()
