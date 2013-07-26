from pyramid.httpexceptions import HTTPFound

from clld.web.adapters.base import Representation, Index


class Redirect(Representation):
    mimetype = 'text/html'
    extension = 'html'

    def render(self, ctx, req):
        raise HTTPFound(
            req.route_url('providers', _anchor='provider-' + req.matchdict['id']))
