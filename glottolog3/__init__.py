from functools import partial

from clld.interfaces import IMenuItems
from clld.web.app import menu_item, get_configurator

from glottolog3 import views
from glottolog3 import models
from glottolog3 import maps
from glottolog3.interfaces import IProvider
from glottolog3.datatables import Families


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['navbar.inverse'] = True
    settings['route_patterns'] = {
        'languages': '/glottolog',
        'language': '/resource/languoid/id/{id:[^/\.]+}',
        #'sources': '/langdoc',
        'provider': '/langdoc/langdocinformation#provider-{id}',
        'providers': '/langdoc/langdocinformation',
    }
    config = get_configurator('glottolog3', settings=settings)
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('languages', partial(menu_item, 'languages', label='Languoids')),
        ('sources', partial(menu_item, 'sources', label='Langdoc')),
    )
    config.register_resource('provider', models.Provider, IProvider)
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
        'glottolog.languages',
        '/glottolog/language',
        views.languages,
        renderer='languages.mako')

    config.add_route_and_view(
        'langdoc',
        '/langdoc',
        views.languages,
        renderer='langdocquery.mako')

    config.add_route_and_view(
        'langdoc.complexquery',
        '/langdoc/complexquery',
        views.languages,
        renderer='langdoccomplexquery.mako')

    config.add_route_and_view(
        'langdoc.meta',
        '/langdoc/langdocinformation',
        views.languages,
        renderer='langdocmeta.mako')

    for name in 'credits glossary cite downloads errata contact'.split():
        pp = '/' if name == 'credits' else '/meta/'
        config.add_route_and_view(
            'home.' + name,
            pp + name,
            getattr(views, name),
            renderer=name + '.mako')

    config.register_map('language', maps.LanguoidMap)
    config.register_datatable('languages', Families)
    return config.make_wsgi_app()
