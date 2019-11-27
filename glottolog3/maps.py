from clld.web.maps import Map, Layer, Legend
from clld.web.adapters.geojson import GeoJson
from clld.web.util.htmllib import HTML, literal

from glottolog3.models import LanguoidLevel


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

    def get_options(self):
        res = {'max_zoom': 12}
        if self.req.matchdict.get('ext') == 'bigmap.html':
            res['hash'] = True
        else:
            res['sidebar'] = True
        res['zoom'] = 4 if self.ctx.level != LanguoidLevel.family else 6
        return res

    def get_legends(self):
        from glottolog3.util import languoid_link

        if self.req.matchdict.get('ext') == 'bigmap.html':
            def value_li(l):
                return (
                    HTML.img(height="20", width="20", src=self.icon_map[l.pk]),
                    literal('&nbsp;'),
                    languoid_link(self.req, l),
                    literal('&nbsp;'),
                    HTML.label(
                        HTML.input(
                            type="checkbox",
                            onclick="GLOTTOLOG3.filterMarkers(this);",
                            class_="checkbox inline",
                            checked="checked",
                            value=str(l.pk)),
                        class_="checkbox inline",
                        title="click to toggle markers"),
                )

            ls = [l for l in self.ctx.children if l.level != LanguoidLevel.dialect]
            if self.ctx.latitude:
                ls = [self.ctx] + ls

            yield Legend(
                self,
                'languoids',
                [value_li(l) for l in ls],
                label='Legend',
                stay_open=True)

        for legend in super(LanguoidMap, self).get_legends():
            yield legend


class MacroareaMap(Map):
    def get_layers(self):
        yield Layer('macroareas', 'macroareas', self.req.route_url('macroareas_geojson'))


def includeme(config):
    config.register_map('language', LanguoidMap)
