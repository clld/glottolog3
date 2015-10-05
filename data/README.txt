
Glottolog update
================

- create directory for new version of files

	(clld)robert@astroman:~/venvs/clld/glottolog3$ mkdir data/2.6

- alembic upgrade head

	alembic upgrade head

- dump current version

	pg_dump -x -O -f data/2.6/glottolog3-before-update.sql glottolog3
    upload downloads of last version + sql dump

- update glottolog-data:

    (clld)robert@astroman:~/venvs/clld/data/glottolog-data$ git pull --rebase origin
    (clld)robert@astroman:~/venvs/clld/data/glottolog-data$ cd scripts
    (clld)robert@astroman:~/venvs/clld/data/glottolog-data/scripts$ time python monster.py

- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini > data/2.6/consistency_before.log

- compute tree changes, update the tree and recompute the tree closure

	time python glottolog3/scripts/compute_tree_changes.py development.ini
2015-10-05 14:32:09,886 INFO  [glottolog3][MainThread] Counter({'matches': 4072, 'new': 25, 'migrations': 12, 'new_languages': 4, 'nomatches': 0})
real	0m26.884s

    Note: Problems with existing names for different hids must be fixed by migrations
    (such as 325a611fee1c) before import of a new tree.

    time python glottolog3/scripts/import_tree.py development.ini
real	5m49.269s

- computing changes again should yield only matches!

    python glottolog3/scripts/compute_tree_changes.py development.ini
2015-07-16 10:14:13,308 INFO  [glottolog3][MainThread] Counter({'matches': 4084, 'new': 0, 'nomatches': 0, 'migrations': 0})

- update refs: First we have to update the data from iso because this may create additional
  refs corresponding to ISO change requests.

    python glottolog3/scripts/load.py development.ini 2.6 iso download
    time python glottolog3/scripts/load.py development.ini 2.6 iso update
matched 23 of 59 macrolangs
real	1m59.957s

    time python glottolog3/scripts/import_refs.py development.ini
2015-07-16 11:35:46,964 INFO  [glottolog3][MainThread] Counter({'updated': 149014, 'new': 5250, 'skipped': 204})
real	78m47.047s

	time python glottolog3/scripts/ia.py development.ini update
2015-07-15 17:24:21,299 INFO  [glottolog3][MainThread] assigned internet archive identifiers for 1490 out of 270158 sources
real	11m1.250s

	time python glottolog3/scripts/gbs.py development.ini update
2015-07-16 11:58:34,482 INFO  [glottolog3][MainThread] assigned gbs ids for 9957 out of 270158 sources
real	11m45.771s

    time python glottolog3/scripts/update_lginfo.py development.ini
2015-07-16 12:02:10,547 WARNI [glottolog3][MainThread] unknown country name in countries.tab: Taiwan
2015-07-16 12:02:11,964 WARNI [glottolog3][MainThread] unknown hid in countries.tab: NOCODE_G\"uenoa
2015-07-16 12:02:13,951 WARNI [glottolog3][MainThread] unknown hid in countries.tab: NOCODE_Jenipapo-Kanind\'e
2015-07-16 12:02:15,224 INFO  [glottolog3][MainThread] countries: 17 relations added
real	3m7.182s

    cp -r data/2.4/unesco/ data/2.6
    time python glottolog3/scripts/load.py development.ini 2.6 unesco update
assigned 2719 unesco urls
missing iso codes: {u'qec': 1, u'qee': 1, u'qed': 1, u'sal': 1, u'qei': 1, u'qej': 1, u'qem': 1, u'qel': 1, u'qvr': 1, u'suf': 1, u'muw': 1, u'gon': 1, u'qhu': 1, u'jap': 1, u'zza': 1, u'wck': 1, u'qan': 1, u'qnt': 1, u'qsa': 1, u'nrn': 1, u'get': 1, u'qln': 1, u'qhj': 1, u'nky': 1, u'qlb': 1, u'wpb': 1, u'cif': 1, u'slb': 1}
real	0m53.475s

    #
    # TODO: run ... download for all data sources below!?
    #
    time python glottolog3/scripts/load.py development.ini 2.6 ethnologue update
2015-07-16 12:10:52,447 INFO  [rdflib][MainThread] RDFLib Version: 4.2.0
384 iso codes have no ethnologue code
1166 of 4084 families have an exact counterpart in ethnologue!
real	0m39.896s

    time python glottolog3/scripts/load.py development.ini 2.6 endangeredlanguages update
2015-07-16 12:11:56,693 INFO  [rdflib][MainThread] RDFLib Version: 4.2.0
assigned 2845 urls
real	0m2.198s

    time python glottolog3/scripts/load.py development.ini 2.6 languagelandscape update
assigned 366 languagelandscape urls
real	0m3.451s

    time python glottolog3/scripts/update_alternative_names.py development.ini
2015-07-16 17:52:23,964 INFO  [glottolog3][MainThread] Counter({'newname': 5, 'newrelation': 5})
real	0m16.420s

    time python glottolog3/scripts/update_reflang.py development.ini
2015-07-16 18:59:39,618 INFO  [glottolog3][MainThread] Counter({u'changed': 8029, u'ignored': 1000, u'obsolete': 558, u'kln': 230, u'NOCODE_Hoa': 28, u'NOCODE_Quechua-Ecuatoriano-Unificado': 14, u'NOCODE_Kwadza': 11, u"NOCODE_Jenipapo-Kanind\\'e": 10, u'NOCODE_Sidi': 10, u'NOCODE_Nauo': 7, u'NOCODE_Quechua-Sureno-Unificado': 5, u'NOCODE_G\\"uenoa': 5, u'kon': 4, u'NOCODE_Wurangung': 4, u'NOCODE_Kenunu': 3, u'kok': 2, u'luy': 2, u'bik': 2, u'iku': 2, u'NOCODE_Nymele': 2, u'NOCODE_Kuvale': 2, u'zha': 2, u'NOCODE_G\xfcenoa': 2, u'NOCODE_Metombola': 1, u'gis/giz': 1, u'yzg/yln': 1, u'yyg': 1, u'sti/stt': 1, u'nxl/nni': 1, u'NOCODE_Jenipapo-Kanind\xe9': 1, u'zps/zpx': 1, u"ils ne comptent que jusqu'\\`a deux": 1, u'gon': 1, u'gpb': 1, u'NOCODE_Esuma': 1, u'ethn': 1, u'though Goedhart states that their accent is quite distinctive.': 1, u'doc/kmc': 1, u'dih?': 1, u'NOCODE_Boshof': 1, u'que': 1, u'NOCODE_Hacha': 1, u'afh': 1, u'mrq/mqm': 1, u'NOCODE_Sakiriaba': 1, u'NOCODE_Mwele': 1, u'and all of the people speak Buginese': 1, u'mmc/maz': 1, u'imperfect speaker of a Harakmbut variety with Pano contamination': 1, u'NOCODE_Akuntsu': 1})
real	66m48.155s

    time python glottolog3/scripts/match_obsolete_refs.py development.ini > data/2.6/obsolete_refs.log


- test feeds of new languages and new grammars!

- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini > data/2.6/consistency_after.log

- update version number!

	python glottolog3/scripts/update_version.py --version=2.6 development.ini

    time python glottolog3/scripts/compute_treefiles.py development.ini
real	3m37.042s

	time python glottolog3/scripts/langdocstatus.py development.ini
real	33m10.481s

    - run nosetests
    - create release of glottolog3
    - create release of glottolog-data

    - create downloads for new version

    time python glottolog3/scripts/create_downloads.py development.ini
real	80m42.376s

    pg_dump -x -O -f glottolog3/static/download/glottolog.sql glottolog3
    gzip glottolog3/static/download/glottolog.sql

    time python glottolog3/scripts/llod.py development.ini
2015-07-17 17:28:44,219 INFO  [glottolog3][MainThread] ... finished
{u'links:geonames': 10733, u'triples': 7393125, u'links:gold': 24333, u'links:lexvo': 7817, u'path': Path(u'/tmp/tmpiEXVz8'), u'links:dbpedia': 7817, u'resources': 393096}
/home/robert/venvs/glottolog3/glottolog3/glottolog3/static/download/glottolog-dataset.n3
>>> Make sure to upload the RDF dump to the production site.
real	203m57.857s

    - deploy to production (copy treefiles and downloads first!?)
    fabg tasks.deploy:production
    fabg tasks.copy_treefiles

    - add dump of new version to glottolog-data
