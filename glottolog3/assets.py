from clld.web.assets import environment
from path import path

import glottolog3

_dir = path(glottolog3.__file__).dirname().joinpath('static')
_url = '/glottolog3:static/'

environment.append_path(_dir, url=_url)
environment.load_path = list(reversed(environment.load_path))
