
# Releasing https://glottolog.org

- Checkout the corresponding release of glottolog/glottolog.
- For major or minor releases: create the static archive including the last release:
  ```shell script
  glottolog-app create_archive
  tar -czf archive.tgz archive/
  ```
- initialize the DB running (about 60 mins)
  ```shell script
  glottolog-app dbinit
  ```
- mark new languages running
  ```shell script
  glottolog-app mark_new_languages
  ```
- remove old downloads:`rm glottolog3/static/download/glottolog*`
- run `clld-create-downloads development.ini` - about 45 mins
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump

- upload downloads to cdstar running `glottolog-app cdstar <release>`
  (if no bitstreams are added to the catalog, the object may need to be re-added via
  cdstarcat, and the above command re-run.)
- register sql dump download in `glottolog3/releases.ini` by adding a new section for the release or
  updating the md5 hash of the sql dump for a bugfix release with the data from downloads.json.
- `clld-llod` ?
- update the landing page with the new ZENODO DOI

- draft release of clld/glottolog3
  - commit all changes to glottolog3
  - create release on GitHub

- Now deploy to server:
```shell script
workon appconfig
cd appconfig/apps
```
**Note**: For new major or minor releases, we must adapt the `dbdump` option in `apps.ini[glottolog3]` 
to the new version.
```shell script
cd appconfig/apps/glottolog3
fab copy_archive:../../../../glottolog/glottolog3/archive.tgz
fab deploy:production
fab fetch_downloads
```

- tweet
