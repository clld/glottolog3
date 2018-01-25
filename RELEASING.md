
# Releasing http://glottolog.org

- Checkout the corresponding release of clld/glottolog.
- update editors
- create the static archive including the last release: `glottolog-app create_archive`
- initialize the DB running `glottolog-app dbinit <release>`
- mark new languages running `glottolog-app mark_new_languages`
- remove old downloads: `rm glottolog3/static/download/glottolog*`
- run `clld-create-downloads development.ini`
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump

- upload downloads to cdstar running `glottolog-app cdstar <release>`
  - download downloads from cdstar to server, for backwards compatibility
- register sql dump download in releases.ini # FIXME!!
- run `glottolog-app ldstatus` to recreate `ldstatus.json`
- `clld-llod` ?

Now deploy to server:
```
workon appconfig
cd appconfig/apps/glottolog3
fab copy_archive:production
fab deploy:production
fab fetch_downloads
```
