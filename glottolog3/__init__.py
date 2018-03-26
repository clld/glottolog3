from functools import partial

import os
from pyramid.httpexceptions import HTTPGone, HTTPMovedPermanently
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.response import Response
from sqlalchemy.orm import joinedload, joinedload_all
from clld.interfaces import ICtxFactoryQuery, IDownload
from clld.web.app import menu_item, CtxFactoryQuery
from clld.web.adapters.base import adapter_factory, Index
from clld.web.adapters.download import N3Dump, Download
from clld.web.adapters.cldf import CldfDownload
from clld.db.models.common import Language, Source, ValueSet, ValueSetReference

import glottolog3
from glottolog3 import views
from glottolog3 import models
from glottolog3 import adapters
from glottolog3.config import CFG
from glottolog3.interfaces import IProvider
from glottolog3.datatables import Providers


class GLCtxFactoryQuery(CtxFactoryQuery):
    def refined_query(self, query, model, req):
        if model == Language:
            query = query.options(
                joinedload(models.Languoid.family),
                joinedload(models.Languoid.children),
                joinedload_all(
                    Language.valuesets, ValueSet.references, ValueSetReference.source)
            )
        return query

    def __call__(self, model, req):
        if model == Language:
            # responses for no longer supported legacy codes
            if not models.Languoid.get(req.matchdict['id'], default=None):
                legacy = models.LegacyCode.get(req.matchdict['id'], default=None)
                if legacy:
                    raise HTTPMovedPermanently(location=legacy.url(req))
            #
            # FIXME: how to serve HTTP 410 for legacy codes?
            #
        elif model == Source:
            if ':' in req.matchdict['id']:
                ref = req.db.query(models.Source)\
                    .join(models.Refprovider)\
                    .filter(models.Refprovider.id == req.matchdict['id'])\
                    .first()
                if ref:
                    raise HTTPMovedPermanently(location=req.route_url('source', id=ref.id))
        return super(GLCtxFactoryQuery, self).__call__(model, req)

def add_cors_headers_response_callback(event):
    # TODO whitelist which sites are allowed Access-Control-Allow-Origin
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings.update(CFG)
    db_url = os.environ.get('GLOTTOLOG_DATABASE_URL')
    if db_url is not None:
        settings['sqlalchemy.url'] = db_url
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
            'Sitemap: {0}\nUser-agent: *\nDisallow: /files/\n'.format(
                req.route_url('sitemapindex')),
            content_type='text/plain'))
    config.registry.registerUtility(GLCtxFactoryQuery(), ICtxFactoryQuery)
    config.register_menu(
        #('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages', label='Languages')),
        ('families', partial(menu_item, 'glottolog.families', label='Families')),
        ('search', partial(menu_item, 'glottolog.languages', label='Language Search')),
        ('sources', partial(menu_item, 'sources', label='References')),
        ('query', partial(menu_item, 'langdoc.complexquery', label='Reference Search')),
        ('about', partial(menu_item, 'about', label='About')),
        # Menu Items created by UW Blueprint
        ('bpsearch', partial(menu_item, 'glottolog.bpsearch', label='Blueprint Search')),
    )
    config.register_resource('provider', models.Provider, IProvider, with_index=True)
    config.register_adapter(
        adapter_factory('provider/index_html.mako', base=Index), IProvider)
    config.add_view(views.redirect_languoid_xhtml, route_name='languoid.xhtml')
    config.add_view(views.redirect_reference_xhtml, route_name='reference.xhtml')
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

    # Endpoints created by UW Blueprint
    config.add_route_and_view(
        'glottolog.bpsearch',
        '/bp/search',
        views.languages,
        renderer='language/bpsearch_html.mako')
    config.add_route(
        'glottolog.bp_api_search',
        'bp/api/search')
    config.add_route(
        'glottolog.add_identifier',
        '/identifiers')
    config.add_route(
        'glottolog.add_languoid',
        '/languoid')
    config.add_route(
        'glottolog.get_languoid',
        '/languoid/{id}')

    # UW blueprint code ends here

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
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    return config.make_wsgi_app()
