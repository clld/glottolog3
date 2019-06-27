import subprocess
import pathlib

import pytest
from sqlalchemy import create_engine
from pyglottolog import Glottolog
from clld.db.meta import DBSession, Base

from glottolog3 import __main__
from glottolog3 import models

TEST_DB = 'glottolog3-test'


@pytest.fixture
def testdb(mocker):
    subprocess.check_call(['dropdb', '-U', 'postgres', '--if-exists', TEST_DB])
    subprocess.check_call(['createdb', '-U', 'postgres', TEST_DB])
    engine = create_engine('postgresql://postgres@/' + TEST_DB)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    mocker.patch('glottolog3.__main__.db_url', mocker.Mock(return_value=engine.url))
    mocker.patch('glottolog3.__main__.with_session')

    yield DBSession
    DBSession.close_all()
    DBSession.remove()
    engine.dispose()
    subprocess.check_call(['dropdb', '-U', 'postgres', '--if-exists', TEST_DB])


def test_dbinit(mocker, testdb, capsys):
    from glottolog3.scripts import check_db_consistency

    args = mocker.Mock(
        repos=Glottolog(pathlib.Path(__file__).parent / 'repos'),
        pkg_dir=pathlib.Path(__file__).parent,
    )
    __main__.dbload(args)
    __main__.dbprime(args)
    assert testdb.query(models.Ref).one().name == 'Huang, Shuanfan 2013'
    check_db_consistency.main(args)
    out, _ = capsys.readouterr()
    assert out.count(': OK') == 15
