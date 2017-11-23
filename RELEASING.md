
# Releasing http://glottolog.org

1. Checkout the corresponding release of clld/glottolog.


3. FIXME: Create list of new refs/languoids, querying the old db.
   - look up previous version in releases.ini
   - compute (new - old) for each criterion

- update version info and editors

7. mark new refs/languoids reading in the lists created in 4.


- create the static archive including the last release: `glottolog-app create_archive`
- update editors, etc.
- initialize the DB running `glottolog-app dbinit <release>`
- run `clld-create-downloads development.ini`
- remove old downloads: `rm glottolog3/static/download/glottolog*`
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump

- upload downloads to cdstar running `glottolog-app cdstar <release>`
- register sql dump download in releases.ini # FIXME!!
- run `glottolog-app ldstatus` to recreate `ldstatus.json`
- `clld-llod` ?

Now deploy to server:
```
workon appconfig
cd appconfig/apps/glottolog3
fab copy_archive:production
fab deploy:production
```

FIXME: run fab task to download downloads from cdstar onto the server!

import os

from six.moves.urllib.request import urlretrieve

from clldutils.jsonlib import load
from clldutils.path import Path


for rel, spec in load('../downloads.json').items():
    print rel
    d = Path(rel)
    if not d.exists():
        d.mkdir()
    for bs in spec['bitstreams']:
        url = 'https://cdstar.shh.mpg.de//bitstreams/{0}/{1}'.format(spec['oid'], bs['bitstreamid'])
        print url
        urlretrieve(url, d.joinpath(bs['bitstreamid'].replace('_', '-')).as_posix())
