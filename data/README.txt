
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
2015-10-05 14:41:19,991 INFO  [glottolog3][MainThread] Counter({'matches': 4097, 'new': 0, 'nomatches': 0, 'migrations': 0})

- update refs: First we have to update the data from iso because this may create additional
  refs corresponding to ISO change requests.

    python glottolog3/scripts/load.py development.ini 2.6 iso download
    time python glottolog3/scripts/load.py development.ini 2.6 iso update
matched 23 of 59 macrolangs
real	1m59.957s

    time python glottolog3/scripts/import_refs.py development.ini
2015-10-05 17:24:16,208 INFO  [glottolog3][MainThread] Counter({'updated': 69510, 'new': 1263, 'skipped': 204})
real	77m46.819s

	time python glottolog3/scripts/ia.py development.ini
2015-10-05 18:46:27,772 INFO  [glottolog3][MainThread] assigned internet archive identifiers for 1489 out of 271075 sources
real	9m47.243s

	time python glottolog3/scripts/gbs.py development.ini
2015-10-05 20:45:48,812 INFO  [glottolog3][MainThread] assigned gbs ids for 9991 out of 271075 sources
real	10m30.581s

    time python glottolog3/scripts/update_lginfo.py development.ini
2015-07-16 12:02:10,547 WARNI [glottolog3][MainThread] unknown country name in countries.tab: Taiwan
2015-07-16 12:02:11,964 WARNI [glottolog3][MainThread] unknown hid in countries.tab: NOCODE_G\"uenoa
2015-07-16 12:02:13,951 WARNI [glottolog3][MainThread] unknown hid in countries.tab: NOCODE_Jenipapo-Kanind\'e
2015-07-16 12:02:15,224 INFO  [glottolog3][MainThread] countries: 17 relations added
real	3m7.182s

    cp -r data/2.4/unesco/ data/2.6
    time python glottolog3/scripts/load.py development.ini 2.6 unesco update
assigned 2719 unesco urls
missing iso codes: {u'qec': 1, u'qee': 1, u'qed': 1, u'sal': 1, u'qei': 1, u'qej': 1, u'qem': 1, u'qel': 1,
                    u'qvr': 1, u'suf': 1, u'muw': 1, u'gon': 1, u'qhu': 1, u'jap': 1, u'zza': 1, u'wck': 1,
                    u'qan': 1, u'qnt': 1, u'qsa': 1, u'nrn': 1, u'get': 1, u'qln': 1, u'qhj': 1, u'nky': 1,
                    u'qlb': 1, u'wpb': 1, u'cif': 1, u'slb': 1}
real	0m49.173s

    #
    # TODO: run ... download for all data sources below!?
    #
    time python glottolog3/scripts/load.py development.ini 2.6 ethnologue update
385 iso codes have no ethnologue code
1164 of 4097 families have an exact counterpart in ethnologue!
real	0m36.368s

    time python glottolog3/scripts/load.py development.ini 2.6 endangeredlanguages update
2015-07-16 12:11:56,693 INFO  [rdflib][MainThread] RDFLib Version: 4.2.0
assigned 2848 urls
real	0m2.337s

    time python glottolog3/scripts/load.py development.ini 2.6 languagelandscape update
assigned 366 languagelandscape urls
real	0m3.298s

    time python glottolog3/scripts/update_alternative_names.py development.ini
2015-10-06 08:51:23,301 INFO  [glottolog3][MainThread] Counter()
real	0m14.727s

    time python glottolog3/scripts/update_reflang.py development.ini
2015-10-06 09:56:22,845 INFO  [glottolog3][MainThread] Counter({
    u'changed': 5282, u'obsolete': 1183, u'ignored': 1000,
    u'kln': 183, u'NOCODE_Hoa': 22, u'NOCODE_Quechua-Ecuatoriano-Unificado': 14,
    u"NOCODE_Jenipapo-Kanind\\'e": 9, u'NOCODE_Sidi': 9, u'NOCODE_Kwadza': 8,
    u'NOCODE_Quechua-Sureno-Unificado': 5, u'NOCODE_G\\"uenoa': 5, u'kok': 2, u'NOCODE_Nauo': 2,
    u'bik': 2, u'iku': 2, u'NOCODE_Kenunu': 2, u'NOCODE_Kuvale': 2, u'NOCODE_G\xfcenoa': 2,
    u'NOCODE_Wurangung': 2, u'NOCODE_Metombola': 1, u'yyg': 1, u'NOCODE_Jenipapo-Kanind\xe9': 1,
    u'zps/zpx': 1, u"ils ne comptent que jusqu'\\`a deux": 1, u'afh': 1, u'kon': 1,
    u'though Goedhart states that their accent is quite distinctive.': 1, u'NOCODE_Boshof': 1,
    u'que': 1, u'mrq/mqm': 1, u'NOCODE_Sakiriaba': 1, u'NOCODE_Mwele': 1, u'and all of the people speak Buginese': 1,
    u'mmc/maz': 1, u'imperfect speaker of a Harakmbut variety with Pano contamination': 1})
real	64m40.647s

    time python glottolog3/scripts/match_obsolete_refs.py development.ini
    time python glottolog3/scripts/fix_consistency.py development.ini


- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini > data/2.6/consistency_after.log

- tests
    - feeds of new languages and new grammars!

- update version number!

	python glottolog3/scripts/update_version.py --version=2.6 development.ini

    time python glottolog3/scripts/compute_treefiles.py development.ini
real	3m37.042s

	time python glottolog3/scripts/langdocstatus.py development.ini
real	33m10.481s

    - run nosetests
    - write changelog, i.e. templates/news.mako
    - create release of glottolog3
    - create release of glottolog-data

    - create downloads for new version

    time python glottolog3/scripts/create_downloads.py development.ini
real	80m42.376s

    - move downloads to new dl dir on server

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
