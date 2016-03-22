
Glottolog update
================

- create directory for new version of files

	(clld)robert@astroman:~/venvs/clld/glottolog3$ mkdir data/2.7

- alembic upgrade head

	alembic upgrade head

- dump current version

	pg_dump -x -O -f data/2.7/glottolog3-before-update.sql glottolog3
    upload downloads of last version + sql dump

- update glottolog-data:

    (clld)robert@astroman:~/venvs/clld/data/glottolog-data$ git pull --rebase origin
    (clld)robert@astroman:~/venvs/clld/data/glottolog-data$ cd scripts
    (clld)robert@astroman:~/venvs/clld/data/glottolog-data/scripts$ time python monster.py

- check consistency

	only 2.7:
		alembic upgrade head
		python glottolog3/scripts/recreate_treeclosure.py development.ini
    python glottolog3/scripts/check_db_consistency.py development.ini > data/2.7/consistency_before.log

- compute tree changes, update the tree and recompute the tree closure

	time python glottolog3/scripts/compute_tree_changes.py development.ini
2016-01-20 15:06:48,537 INFO  [glottolog3][MainThread] Counter({'matches': 4091, 'new': 23, 'new_languages': 8, 'migrations': 7, 'nomatches': 0})

    Note: Problems with existing names for different hids must be fixed by migrations
    (such as 325a611fee1c) before import of a new tree.

    time python glottolog3/scripts/import_tree.py development.ini
real	5m49.269s

- computing changes again should yield only matches!

    python glottolog3/scripts/compute_tree_changes.py development.ini
2016-01-20 15:13:38,106 WARNI [glottolog3][MainThread] no leafs! (35802, {u'hname': u'West Palaungic'}, u'custom', u'pala1335', u'Palaung-Riang', None, None, None, None, datetime.datetime(2016, 1, 20, 15, 7, 32, 185563, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=60, name=None)), True, datetime.datetime(2013, 5, 2, 21, 32, 10, 849467, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=120, name=None)), 1, 35802, None, 105149, 104956, <family>, <established>, 0, 0, 0)
2016-01-20 15:13:54,803 INFO  [glottolog3][MainThread] Counter({'matches': 4112, 'new': 0, 'nomatches': 0, 'migrations': 0})

- update refs: First we have to update the data from iso because this may create additional
  refs corresponding to ISO change requests.

    python glottolog3/scripts/load.py development.ini 2.7 iso download
    time python glottolog3/scripts/load.py development.ini 2.7 iso update
matched 24 of 59 macrolangs
real	1m59.957s

    time python glottolog3/scripts/import_refs.py development.ini
2016-01-20 16:17:14,470 INFO  [glottolog3][MainThread] Counter({'updated': 63492, 'new': 4470, 'skipped': 204})
real	57m49.631s

	time python glottolog3/scripts/ia.py development.ini
2016-01-20 16:36:43,193 INFO  [glottolog3][MainThread] assigned internet archive identifiers for 1489 out of 275369 sources
real	10m27.608s

	time python glottolog3/scripts/gbs.py development.ini
2016-01-20 16:48:53,302 INFO  [glottolog3][MainThread] assigned gbs ids for 9990 out of 275369 sources
real	11m21.013s

    time python glottolog3/scripts/update_lginfo.py development.ini
Counter({u'justifications-subclassification': 71, u'macroarea': 60, u'coordinates_changed': 13, u'coordinates_new': 8, u'countries': 8, u'justifications-family': 8})
real	3m14.868s

    cp -r data/2.7/unesco/ data/2.7
    time python glottolog3/scripts/load.py development.ini 2.7 unesco update
assigned 2719 unesco urls
missing iso codes: {u'qec': 1, u'qee': 1, u'qed': 1, u'sal': 1, u'qei': 1, u'qej': 1, u'qem': 1, u'qel': 1, u'qvr': 1, u'suf': 1, u'muw': 1, u'gon': 1, u'qhu': 1, u'jap': 1, u'zza': 1, u'wck': 1, u'qan': 1, u'qnt': 1, u'qsa': 1, u'nrn': 1, u'get': 1, u'qln': 1, u'qhj': 1, u'nky': 1, u'qlb': 1, u'wpb': 1, u'cif': 1, u'slb': 1}
real	0m52.702s

    #
    # TODO: run ... download for all data sources below!?
    #
    time python glottolog3/scripts/load.py development.ini 2.7 ethnologue update
388 iso codes have no ethnologue code
1159 of 4114 families have an exact counterpart in ethnologue!
real	0m36.688s

    time python glottolog3/scripts/load.py development.ini 2.7 endangeredlanguages update
2015-07-16 12:11:56,693 INFO  [rdflib][MainThread] RDFLib Version: 4.2.0
assigned 2848 urls
real	0m2.337s

    time python glottolog3/scripts/load.py development.ini 2.7 languagelandscape update
assigned 367 languagelandscape urls
real	0m2.773s

    time python glottolog3/scripts/update_alternative_names.py development.ini
2015-10-06 08:51:23,301 INFO  [glottolog3][MainThread] Counter()
real	0m14.727s

    time python glottolog3/scripts/update_reflang.py development.ini
2016-01-26 10:39:44,054 INFO  [glottolog3][MainThread] Counter(
{u'changed': 3830, u'obsolete': 2388, u'ignored': 1000,
u'kln': 183, u'NOCODE_Hoa': 22, u'NOCODE_Quechua-Ecuatoriano-Unificado': 14,
u"NOCODE_Jenipapo-Kanind\\'e": 9, u'NOCODE_Sidi': 9, u'NOCODE_Kwadza': 8, u'NOCODE_G\\"uenoa': 6,
u'NOCODE_Quechua-Sureno-Unificado': 5, u'kok': 2, u'NOCODE_Nauo': 2, u'bik': 2, u'iku': 2,
u'NOCODE_Kenunu': 2, u'NOCODE_Kuvale': 2, u'NOCODE_G\xfcenoa': 2, u'NOCODE_Wurangung': 2,
u'cultivator)': 1, u'yyg': 1, u'NOCODE_Jenipapo-Kanind\xe9': 1, u'zps/zpx': 1,
u"ils ne comptent que jusqu'\\`a deux": 1, u'digger and navvy)': 1, u'afh': 1, u'kon': 1,
u'NOCODE_Metombola': 1, u'though Goedhart states that their accent is quite distinctive.': 1,
u'NOCODE_Boshof': 1, u'que': 1, u'mrq/mqm': 1, u'NOCODE_Sakiriaba': 1, u'NOCODE_Mwele': 1,
u'and all of the people speak Buginese': 1, u'mmc/maz': 1,
u'imperfect speaker of a Harakmbut variety with Pano contamination': 1})
real	64m40.647s


    time python glottolog3/scripts/match_obsolete_refs.py development.ini
2016-01-26 10:52:50,007 INFO  [glottolog3][MainThread] 219 replacements
real	0m27.111s

    time python glottolog3/scripts/fix_consistency.py development.ini


- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini > data/2.7/consistency_after.log

- tests
    - feeds of new languages and new grammars!

- update version number!

	python glottolog3/scripts/update_version.py --version=2.7 development.ini

    time python glottolog3/scripts/compute_treefiles.py development.ini
real	3m37.042s

	time python glottolog3/scripts/langdocstatus.py development.ini
real	33m10.481s

    pg_dump -x -O -f glottolog3/static/download/glottolog.sql glottolog3
    gzip glottolog3/static/download/glottolog.sql


    - run nosetests
    - write changelog, i.e. templates/news.mako
    - create release of glottolog3
    - add dump of new version to glottolog-data
    - push changes to glottolog-data
    - create release of glottolog-data
    - create downloads for new version

    time python glottolog3/scripts/create_downloads.py development.ini
real	80m42.376s

    - move downloads to new dl dir on server

    time python glottolog3/scripts/llod.py development.ini
2015-07-17 17:28:44,219 INFO  [glottolog3][MainThread] ... finished
{u'links:geonames': 10733, u'triples': 7393125, u'links:gold': 24333, u'links:lexvo': 7817, u'path': Path(u'/tmp/tmpiEXVz8'), u'links:dbpedia': 7817, u'resources': 393096}
/home/robert/venvs/glottolog3/glottolog3/glottolog3/static/download/glottolog-dataset.n3
>>> Make sure to upload the RDF dump to the production site.
real	203m57.857s

    - deploy to production (copy treefiles and downloads first!?)
    fab tasks.deploy:production
    fab copy_treefiles
    copy downloads from download/2.7 to download

	- update github releases with DOI from ZENODO

    - tweet
