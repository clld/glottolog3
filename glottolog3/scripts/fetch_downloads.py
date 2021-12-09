"""
Script called from a fab task (running on the server) to fetch downloads after deploying
a new release.
"""
from urllib.request import urlretrieve

from clldutils.jsonlib import load
from clldutils.path import Path, md5

import glottolog3

DOWNLOAD_DIR = Path(glottolog3.__file__).parent.joinpath('static', 'download')

for rel, spec in load(DOWNLOAD_DIR.parent / 'downloads.json').items():
    d = DOWNLOAD_DIR / rel
    if not d.exists():
        d.mkdir()
    for bs in spec['bitstreams']:
        url = 'https://cdstar.eva.mpg.de//bitstreams/{0}/{1}'.format(
            spec['oid'], bs['bitstreamid'])
        target = d.joinpath(bs['bitstreamid'].replace('_', '-'))
        if (not target.exists()) or bs['checksum'] != md5(target):
            print('retrieving {0} {1}'.format(rel, target))
            urlretrieve(url, str(target))
