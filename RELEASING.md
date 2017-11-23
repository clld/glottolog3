
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
- run `python glottolog3/scripts/langdocstatus.py development.ini` to recreate `ldstatus.json`
- `clld-llod` ?

- run `fab tasks.copy_files:production` to copy the static archive to the server.
- run `fab tasks.deploy:production` to copy new code and database to the server.
