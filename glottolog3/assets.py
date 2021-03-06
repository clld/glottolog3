from clld.web.assets import environment
from pathlib import Path

import glottolog3

_dir = Path(glottolog3.__file__).parent / 'static'
_url = '/glottolog3:static/'

environment.append_path(str(_dir), url=_url)
environment.load_path = list(reversed(environment.load_path))
