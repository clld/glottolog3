from functools import partial

from pyramid.response import Response
from clld.interfaces import IMenuItems, ILanguage
from clld.web.app import menu_item, get_configurator
from clld.web.adapters.base import adapter_factory, Index
from clld.web.adapters.download import CsvDump, N3Dump, Download, RdfXmlDump
from clld.db.models.common import Language, Source

from glottolog3 import views
from glottolog3 import models
from glottolog3 import maps
from glottolog3 import adapters
from glottolog3 import datatables
from glottolog3.config import CFG
from glottolog3.interfaces import IProvider


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings.update(CFG)
    settings['navbar.inverse'] = True
    settings['route_patterns'] = {
        'languages': '/glottolog',
        'language': '/resource/languoid/id/{id:[^/\.]+}',
        'source': '/resource/reference/id/{id:[^/\.]+}',
        'sources': '/langdoc',
        #'provider': '/langdoc/langdocinformation#provider-{id}',
        'providers': '/langdoc/langdocinformation',
    }
    settings['sitemaps'] = ['language', 'source']
    config = get_configurator(
        'glottolog3',
        settings=settings,
        routes=[
            ('languoid.xhtml', '/resource/languoid/id/{id:[^/\.]+}.xhtml'),
            ('reference.xhtml', '/resource/reference/id/{id:[^/\.]+}.xhtml')])
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages', label='Languoids')),
        ('sources', partial(menu_item, 'sources', label='Langdoc')),
    )
    config.register_resource('provider', models.Provider, IProvider, with_index=True)
    config.register_adapter(adapters.Redirect, IProvider)
    config.register_adapter(adapters.Bigmap, ILanguage)
    config.register_adapter(adapter_factory('provider/index_html.mako', base=Index), IProvider)
    config.register_datatable('providers', datatables.Providers)

    config.add_view(views.redirect_languoid_xhtml, route_name='languoid.xhtml')
    config.add_view(views.redirect_reference_xhtml, route_name='reference.xhtml')

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
        '/glottolog/language',
        views.languages,
        renderer='languages.mako')

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

    for name in 'credits glossary cite downloads errata contact'.split():
        pp = '/' if name == 'credits' else '/meta/'
        config.add_route_and_view(
            'home.' + name,
            pp + name,
            getattr(views, name),
            renderer=name + '.mako')

    config.register_map('language', maps.LanguoidMap)
    config.register_datatable('languages', datatables.Families)
    config.register_datatable('sources', datatables.Refs)

    config.register_download(CsvDump(
        Language, 'glottolog3', description="Languoids as CSV"))
    config.register_download(RdfXmlDump(
        Language, 'glottolog3', description="Languoids as RDF"))
    config.register_download(Download(
        Source, 'glottolog3', ext='bib', description="References as BibTeX"))
    config.register_download(RdfXmlDump(
        Source, 'glottolog3', description="References as RDF"))
    return config.make_wsgi_app()
