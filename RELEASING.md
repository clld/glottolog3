# Releasing https://glottolog.org

On `dlceutil` as user `glottolog` (where `monster.bib` should have been created before):

- Checkout the corresponding release of glottolog/glottolog:
  ```shell
  glgit checkout v5.5
  ```

- For major or minor releases: create the static archive of the current version:
  ```shell
  glapp_create_archive 5.4 --out archive
  ```
  Then create a new version of https://doi.org/10.5281/zenodo.23421523, copy the files from
  the previous version, save as draft and upload the new files using the new deposit ID:
  ```shell
  export USER="token"
  mediautils_upload_to_zenodo <deposit_id> <USER> --dir archive
  ```

- Initialize the app DB running (about 60 mins)
  ```shell
  clld_initdb
  ```

- Create downloads (about 45 mins)
  ```shell
  clld_create_downloads --out 5.4
  glapp_create_downloads 5.4
  ```
  create a new version of the Zenodo deposit https://doi.org/10.5281/zenodo.21676495
  with appropriate version setting and note the new deposit ID.
  ```shell
  export USER="token"
  mediautils_upload_to_zenodo <did> <USER> --dir .
  ```
  Release the new version.

- register the downloads by filling in the `doi` item for the version in `static/downloads.json`

- draft release of clld/glottolog3
  - commit and push all changes to glottolog3
  - create release on GitHub

- Checkout master
  ```shell
  glgit checkout master
  ```


On `localhost`:

- Now deploy to server: 
  update `app_dbdump` variable in appconfig
  ```shell
  appconfig appfetchwww glottolog
  appconfig appdeploy glottolog --withdb
  ```
  and check archive:
  ```
  curl -I https://glottolog.org/resource/languoid/id/aban1244
HTTP/1.1 301 Moved Permanently
  ```
- tweet
