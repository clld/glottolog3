
# Releasing https://glottolog.org

- Checkout the corresponding release of glottolog/glottolog.
- For major or minor releases: create the static archive including the last release:
  ```shell
  glottolog-app create_archive 5.3 path/to/download/of/glottocode2version.json --out ../archive/
  ```
  Then create a new version of https://doi.org/10.5281/zenodo.23421523 and add the files.

On `dlceutil` as user `glottolog` (where `monster.bib` should have been created before):

- initialize the DB running (about 60 mins)
  ```shell
  cd glottolog3
  clld_initdb
  ```
- remove old downloads:
  ```shell
  rm glottolog3/static/download/*
  ```
- run (about 45 mins)
  ```shell
  clld_create_downloads
  glapp_newick
  glapp_geo
  glapp_sqldump
  cp -r glottolog3/static/download/ /tmp/<version>
  ```
  create a new version of the Zenodo deposit https://doi.org/10.5281/zenodo.21676495
  with appropriate version setting and note the new deposit ID.
  ```shell
  /usr/venvs/mediautils/bin/mediautils upload_to_zenodo <did> /tmp
  ```
  Release the new version.

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
