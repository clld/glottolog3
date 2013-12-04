from collections import OrderedDict

from clld.web.maps import Map, Layer, Legend
from clld.web.adapters.geojson import GeoJson, pacific_centered_coordinates
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import JS

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

    def get_coordinates(self, language):
        return pacific_centered_coordinates(language)


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
        if self.req.matchdict.get('ext') == 'bigmap.html':
            return {'max_zoom': 12, 'hash': True}
        return {'sidebar': True}

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


COLOR_MAP = OrderedDict()
COLOR_MAP['green'] = ("00ff00", 'a grammar')
COLOR_MAP['orange'] = ("ff8040", 'a grammar sketch')
COLOR_MAP['orange red'] = ("ff4500", 'a dictionary, phonology, specific feature, text or new testament')
COLOR_MAP['red'] = ("ff0000", 'something less')
COLOR_MAP['dark green'] = ("006400", '')
COLOR_MAP['light gray'] = ("d3d3d3", '')
COLOR_MAP['slate gray'] = ("708a90", '')
COLOR_MAP['black'] = ("000000", '')


class DescStatsGeoJson(GeoJson):
    def __init__(self, obj, icon_map=None):
        super(DescStatsGeoJson, self).__init__(obj)
        self.icon_map = None

    def feature_iterator(self, ctx, req):
        return ctx.values()

    def featurecollection_properties(self, ctx, req):
        return {'layer': 'desc'}

    def get_icon(self, type_=None, extinct_mode=False):
        icon = self.icon_map['black'] if extinct_mode else self.icon_map['red']
        if type_ == 'grammar':
            icon = self.icon_map['dark green'] if extinct_mode else self.icon_map['green']
        elif type_ == 'grammarsketch':
            icon = self.icon_map['light gray'] if extinct_mode else self.icon_map['orange']
        elif type_ in 'dictionary phonology specificfeature text newtestament'.split():
            icon = self.icon_map['slate gray'] if extinct_mode else self.icon_map['orange red']
        return icon

    def feature_properties(self, ctx, req, feature):
        if not self.icon_map:
            self.icon_map = {}
            for name, spec in COLOR_MAP.items():
                color, desc = spec
                self.icon_map[name] = req.static_url('glottolog3:static/icons/c%s.png' % color)

        # augment the source dicts
        for s in feature['sources']:
            s['eicon'] = s['icon'] = self.get_icon(s['doctype'])
            if feature['extinct']:
                s['eicon'] = self.get_icon(s['doctype'], extinct_mode=True)

        med = feature['med']
        eicon = icon = self.get_icon(med['doctype'] if med else None)
        if feature['extinct']:
            eicon = self.get_icon(med['doctype'] if med else None, extinct_mode=True)
        red_eicon = red_icon = self.icon_map['red']
        if feature['extinct']:
            red_eicon = self.icon_map['black']
        return {
            'icon': icon,
            'eicon': eicon,
            'med': med['id'] if med else None,
            'info_query': {'source': med['id']} if med else {},
            'red_icon': red_icon,
            'red_eicon': red_eicon,
            'sources': feature['sources']}

    def get_language(self, ctx, req, feature):
        return Language(
            0, feature['name'], feature['longitude'], feature['latitude'], feature['id'])

    def get_coordinates(self, language):
        return pacific_centered_coordinates(language)


class DescStatsMap(Map):
    def get_layers(self):
        yield Layer(
            'languoids',
            'Languoids',
            DescStatsGeoJson(self.ctx).render(self.ctx, self.req, dump=False))

    def get_options(self):
        return {
            'icon_size': 20,
            'hash': True,
            'on_init': JS('GLOTTOLOG3.descStatsUpdateIcons'),
            'no_showlabels': True}

    def get_legends(self):
        def img(color):
            return HTML.img(
                src=self.req.static_url(
                    'glottolog3:static/icons/c%s.png' % COLOR_MAP[color][0]),
                height='20',
                width='20',
                style='margin-left: 0.5em;')

        def desc(color, text=None):
            return HTML.span(
                text or COLOR_MAP[color][1], style='margin-left: 0.5em; margin-right: 0.5em;')

        values = [
            desc(None, 'Most extensive description is ...'),
            (img('green'), img('dark green'), desc('green')),
            (img('orange'), img('light gray'), desc('orange')),
            (img('orange red'), img('slate gray'), desc('orange red')),
            (img('red'), img('black'), desc('red')),
        ]
        yield Legend(self, 'values', values, label='Legend')
