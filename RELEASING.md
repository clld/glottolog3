
- checkout release of clld/glottolog
- initialize the DB running `glottolog-app dbinit 3.0`
- run `clld-create-downloads development.ini`
- run `glottolog-app downloads` to create
  - global newick tree
  - languages_and_dialects_geo.csv
  - gzipped db dump
  - upload downloads to cdstar
- `clld-llod` ?
- run `fab tasks.copy_files:production` to copy the static archive to the server.

