
# Releasing https://glottolog.org

- Checkout the corresponding release of glottolog/glottolog.
- For major or minor releases: create the static archive including the last release:
  ```shell
  cd ../archive
  glottolog-app create_archive
  tar -czf archive.tgz archive/
  ```
- initialize the DB running (about 60 mins)
  ```shell
  cd ../glottolog3
  clld initdb development.ini
  ```
  and check language associations, see e.g. https://github.com/glottolog/glottolog/issues/485
- mark new languages running
  ```shell
  glottolog-app mark_new_languages
  pytest
  ```
- remove old downloads:`rm glottolog3/static/download/glottolog*`
- run `clld create_downloads development.ini glottolog.org` - about 45 mins
- run
  ```shell
  glottolog-app newick
  glottolog-app geo development.ini
  glottolog-app sqldump development.ini
  ``` 
  to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump

- upload downloads to cdstar running `glottolog-app cdstar <release>`
  if no bitstreams are added to the catalog, the object may need to be re-added via
  cdstarcat, and the above command re-run. To do so,
  - look for "glottolog <release>" in https://cdstar.eva.mpg.de and note the OID
  - run `cdstarcat add EAEA0-...` (or `cdstarcat add EA... --update` later)
  - run `glottolog-app cdstar <release> --oid <OID>`
- register sql dump download in `glottolog3/releases.ini` by adding a new section for the release or
  updating the md5 hash of the sql dump for a bugfix release with the data from downloads.json.
- update `glottolog3.util.DOI` with the new ZENODO DOI

- draft release of clld/glottolog3
  - commit all changes to glottolog3
  - create release on GitHub

- Now deploy to server:
  ```shell
  workon appconfig
  cd appconfig/apps
  ```
  **Note**: For new major or minor releases, we must adapt the `dbdump` option in `apps.ini[glottolog3]` 
  to the new version.
  ```shell
  cd appconfig/apps/glottolog3
  fab copy_archive:../../../../glottolog/archive/archive.tgz
  fab deploy:production
  fab fetch_downloads
  ```
  and check archive:
  ```
  curl -I https://glottolog.org/resource/languoid/id/aban1244
HTTP/1.1 301 Moved Permanently
  ```
- tweet
