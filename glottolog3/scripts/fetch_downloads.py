# coding: utf8
from __future__ import unicode_literals, print_function, division

from six.moves.urllib.request import urlretrieve

from clldutils.jsonlib import load
from clldutils.path import Path

import glottolog3

DOWNLOAD_DIR = Path(glottolog3.__file__).parent.joinpath('static', 'download')

for rel, spec in load(DOWNLOAD_DIR.parent / 'downloads.json').items():
    d = DOWNLOAD_DIR / rel
    if not d.exists():
        d.mkdir()
    for bs in spec['bitstreams']:
        url = 'https://cdstar.shh.mpg.de//bitstreams/{0}/{1}'.format(
            spec['oid'], bs['bitstreamid'])
        target = d.joinpath(bs['bitstreamid'].replace('_', '-'))
        if not target.exists():
            print('retrieving {0} {1}'.format(rel, target))
            urlretrieve(url, str(target))
