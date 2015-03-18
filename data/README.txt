
Glottolog update
================

- create directory for new version of files

	(clld)robert@astroman:~/venvs/clld/glottolog3$ mkdir data/2.4

- update glottolog-data:

    (clld)robert@astroman:~/venvs/clld/data/glottolog-data/scripts$ git pull --rebase origin
    (clld)robert@astroman:~/venvs/clld/data/glottolog-data/scripts$ time python monster.py

- copy files

    (clld)robert@astroman:~/venvs/clld/data/glottolog-data/scripts$ t
	(clld)robert@astroman:~/venvs/clld/harald_ftp$ ./copy.sh 2.4

- alembic upgrade head

	alembic upgrade head

- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini

- dump current version

	pg_dump -x -O -f data/2.4/glottolog3-before-update.sql glottolog3
    upload downloads of last version + sql dump

- compute tree changes, update the tree and recompute the tree closure

	python glottolog3/scripts/compute_tree_changes.py --version=2.4 development.in
        3830 matches
        52 migrations
        0 nomatches
        219 new nodes
        76 new languages

    Note: Problems with existing names for different hids must be fixed by migrations
    before import of a new tree.

    python glottolog3/scripts/import_tree.py --version=2.4 development.ini
        real	9m15.198s

- computing changes again should yield only matches!

    python glottolog3/scripts/compute_tree_changes.py --version=2.4 development.ini

        ~~ Ghera-Gurgula -> Indo-European, Indo-Iranian, Indo-Aryan, Indo-Aryan Central zone, Subcontinental Central Indo-Aryan, Western Hindi, Unclassified Western Hindi, Ghera-Gurgula
        ~~ Chinali-Lahul Lohar -> Indo-European, Indo-Iranian, Indo-Aryan, Unclassified Indo-Aryan, Chinali-Lahul Lohar
        -- Yucatecan-Core Mayan ->
        4046 matches
        2 migrations
        1 nomatches
        0 new nodes
        0 new languages

- update refs:

    #remove obsolete refs, i.e. refs no longer in monster.bib.
    #    - create bibtex, store in github repo
    #    - create obsolete_refs_matches.json
    #    - remove refs with matches
    #python glottolog3/scripts/match_obsolete_refs.py --version=2.4 development.ini
    python glottolog3/scripts/import_refs.py --version=2.4 --mode=update development.ini

	python glottolog3/scripts/ia.py development.ini update
	python glottolog3/scripts/gbs.py development.ini update

    #
    # TODO: run ... download for all data sources below!?
    #
    python glottolog3/scripts/load.py development.ini 2.4 hh update
    #python glottolog3/scripts/load.py development.ini 2.4 glottologcurator update
    python glottolog3/scripts/load.py development.ini 2.4 unesco update
    python glottolog3/scripts/load.py development.ini 2.4 ethnologue update
    python glottolog3/scripts/load.py development.ini 2.4 iso update
    python glottolog3/scripts/load.py development.ini 2.4 endangeredlanguages update
    python glottolog3/scripts/load.py development.ini 2.4 languagelandscape update
    #python glottolog3/scripts/load.py development.ini 2.4 wikipedia update

    python glottolog3/scripts/update_alternative_names.py development.ini
    python glottolog3/scripts/update_reflang.py --version=2.4 development.ini

    #unknown codes [u'ipk', u'yyg', u'qpt', u'hai', u'kok', u'gon', u'NOCODE_Kenunu', u'yrm', u'kon', u'gpb', u'adc', u'NOCODE_Metombola', u'tmh', u'NOCODE_Kwadza', u'bik', u'iku', u'NOCODE_Teshena', u'NOCODE_Nymele', u'uwu', u'NOCODE_Sidi', u'psx', u'NOCODE_Boshof', u'que', u'NOCODE_Hacha', u'afh', u'NOCODE_Sakiriaba', u'NOCODE_Mwele', u'din', u'NOCODE_Auyo', u'NOCODE_Kuvale', u'kln', u'gny', u'sqi', u'idn', u'ful', u'NOCODE_Wurangung']

    python glottolog3/scripts/compute_treefiles.py development.ini
	python glottolog3/scripts/langdocstatus.py development.ini

- test feeds of new languages and new grammars!

- check consistency

    python glottolog3/scripts/check_db_consistency.py development.ini

- update version number!

    TODO: update editors! Sebastian Bank statt Nordhoff!

	python glottolog3/scripts/update_version.py --version=2.4 development.ini


    - run nosetests
    - tag code

    - create downloads for new version
    - deploy to production (copy treefiles and downloads first!?)
    - add dump of new version to glottolog-data


TODO: fix
- http://localhost:6543/glottolog/glottologinformation
- http://localhost:6543/news
