import logging
import pathlib
import subprocess

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from clld.db.meta import DBSession, Base

from glottolog3 import models
from glottolog3.__main__ import main

TEST_DB = 'glottolog3-test'


@pytest.fixture
def repos():
    return pathlib.Path(__file__).parent / 'repos'


@pytest.fixture
def testdb(mocker):
    subprocess.check_call(['dropdb', '-U', 'postgres', '--if-exists', TEST_DB])
    subprocess.check_call(['createdb', '-U', 'postgres', TEST_DB])
    engine = create_engine('postgresql://postgres@/' + TEST_DB)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    yield DBSession
    close_all_sessions()
    DBSession.remove()
    engine.dispose()
    subprocess.check_call(['dropdb', '-U', 'postgres', '--if-exists', TEST_DB])


def test_dbinit(mocker, testdb, capsys, repos):
    from glottolog3.scripts import check_db_consistency
    from glottolog3.scripts import initializedb

    mocker.patch(
        'glottolog3.scripts.initializedb.assert_release', mocker.Mock(return_value='1.0'))
    initializedb.main(mocker.Mock(), repos=repos)
    initializedb.prime_cache(mocker.Mock(), repos=repos)
    assert testdb.query(models.Ref).one().name == 'Huang, Shuanfan 2013'
    check_db_consistency.main(mocker.Mock())
    out, _ = capsys.readouterr()
    assert out.count(': OK') == 15


def test_newick(tmpdir, repos):
    main(['--repos', str(repos), 'newick', '--output', str(tmpdir.join('test'))],
         log=logging.getLogger(__name__))
    assert pathlib.Path(str(tmpdir)).joinpath('test').exists()
