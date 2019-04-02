
# Releasing http://glottolog.org

- Checkout the corresponding release of clld/glottolog.
- update editors in glottolog3/initdb.py
- For major or minor releases: create the static archive including the last release:
  ```bash
  glottolog-app create_archive
  tar -czf archive.tgz archive/
  ```
- initialize the DB running (about 50 mins)
  ```bash
  glottolog-app dbinit <release>
  ```
- mark new languages running
  ```bash
  glottolog-app mark_new_languages <release>
  ```
- remove old downloads:`rm glottolog3/static/download/glottolog*`
- run `clld-create-downloads development.ini` - about 45 mins
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump

- upload downloads to cdstar running `glottolog-app cdstar <release>`
- register sql dump download in releases.ini by adding a new section for the release or
  updating the md5 hash of the sql dump for a bugfix release with the data from downloads.json.
- run `glottolog-app ldstatus` to recreate `ldstatus.json`
- `clld-llod` ?

- draft release of clld/glottolog3
  - commit all changes to glottolog3
  - tag a release
  - push to GitHub
  - create release on GitHub
- edit release adding the zenodo DOI badge
  - to the release description
  - to the landing page of glottolog.org

- Now deploy to server:
```
workon appconfig
cd appconfig/apps
```
For new major of minor releases, we must adapt the `dbdump` option in `apps.ini[glottolog3]` 
to the new version.
```
cd appconfig/apps/glottolog3
fab copy_archive:/path/to/archive.tgz
fab deploy:production
fab fetch_downloads
```

- tweet
