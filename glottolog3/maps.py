from clld.web.maps import Map, Layer
from clld.web.adapters import GeoJson
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import link
from clld.interfaces import IIcon


class Language(object):
    def __init__(self, pk, name, longitude, latitude, id_):
        self.pk = pk
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.id = id_

    def __json__(self, req):
        return self.__dict__


class LanguoidGeoJson(GeoJson):
    def __init__(self, obj, icon_map=None):
        super(LanguoidGeoJson, self).__init__(obj)
        self.icon_map = icon_map or {}

    def feature_iterator(self, ctx, req):
        res = [(ctx.pk, ctx.name, ctx.longitude, ctx.latitude, ctx.id)] \
            if ctx.latitude else []
        return res + list(ctx.get_geocoords())

    def featurecollection_properties(self, ctx, req):
        return {'layer': getattr(ctx, 'id', '')}

    def feature_properties(self, ctx, req, feature):
        if self.icon_map:
            return {'icon': self.icon_map[feature[0]], 'branch': feature[0]}
        return {}

    def get_language(self, ctx, req, feature):
        return Language(*feature)


class LanguoidMap(Map):
    def __init__(self, ctx, req, eid='map', icon_map=None):
        super(LanguoidMap, self).__init__(ctx, req, eid=eid)
        self.icon_map = icon_map or {}

    def get_layers(self):
        yield Layer(
            self.ctx.id,
            self.ctx.name,
            LanguoidGeoJson(
                self.ctx, self.icon_map).render(self.ctx, self.req, dump=False))

    def options(self):
        return {'sidebar': self.req.matched_route.name != 'glottolog.languoid_bigmap'}

    def legend(self):
        if self.req.matched_route.name == 'glottolog.languoid_bigmap':
            def value_li(l):
                return HTML.li(
                    HTML.label(
                        HTML.img(
                            height="20",
                            width="20",
                            src=self.icon_map[l.id]),
                        literal('&nbsp;'),
                        HTML.a(
                            l.primaryname,
                            class_="Languoid %s" % l.level,
                            href=self.req.resource_url(l)),
                        style='margin-left: 1em; margin-right: 1em;'))

            ls = [l for l in self.ctx.children if l.level != 'dialect']
            if self.ctx.latitude:
                ls = [self.ctx] + ls
            return HTML.li(
                HTML.a(
                    'Legend',
                    HTML.b(class_='caret'),
                    **{'class': 'dropdown-toggle', 'data-toggle': "dropdown", 'href': "#"}
                ),
                HTML.ul(*[value_li(l) for l in ls], class_='dropdown-menu'),
                class_='dropdown'
            )
        return ''


class LanguoidsGeoJson(LanguoidGeoJson):
    def feature_iterator(self, ctx, req):
        return [
            (l.pk, l.name, l.longitude, l.latitude, l.id)
            for l in ctx if l.latitude]


class LanguoidsMap(LanguoidMap):
    def get_layers(self):
        yield Layer(
            'languoids',
            'Languoids',
            LanguoidsGeoJson(self.ctx).render(self.ctx, self.req, dump=False))
