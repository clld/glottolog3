import pytest

import sqlalchemy as sa
import pyramid.paster


@pytest.fixture(scope='session')
def appini(pytestconfig):
    return pytestconfig.getoption('appini')


@pytest.fixture(scope='session')
def settings(appini):
    return pyramid.paster.get_appsettings(appini)


@pytest.fixture(scope='session')
def data(settings):
    from clld.db.meta import Base, DBSession

    engine = sa.engine_from_config(settings)
    Base.metadata.create_all(bind=engine)
    DBSession.configure(bind=engine)

    yield engine

    DBSession.close()

