
- checkout release of clld/glottolog
- initialize the DB running `glottolog-app dbinit 3.0`
- run `clld-create-downloads development.ini`
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump
  - upload downloads to cdstar  # FIXME!!
- run `python glottolog3/scripts/langdocstatus.py development.ini` to recreate `ldstatus.json`
- `clld-llod` ?

- run `fab tasks.copy_files:production` to copy the static archive to the server.
- run `fab tasks.copy_downloads:production` to copy the static archive to the server.
- run `fab tasks.deploy:production` to copy the static archive to the server.

- create static pages for languoids
  TODO: `static_archive.py` should be turned into a command.
