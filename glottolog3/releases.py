import gzip
import shutil
import pathlib
import subprocess
from urllib.request import urlretrieve

from clldutils.db import DB
from clldutils.path import md5
import attr


@attr.s
class Release:
    tag = attr.ib()
    version = attr.ib()
    cdstar_oid = attr.ib()
    sql_dump_md5 = attr.ib()
    sql_dump_url = attr.ib()

    @classmethod
    def from_config(cls, cfg, section):
        return cls(tag=section, **cfg[section])

    def dump_fname(self, zipped=False):
        return pathlib.Path('glottolog-{0}.sql{1}'.format(self.version, '.gz' if zipped else ''))

    def download_sql_dump(self, log):
        target = self.dump_fname(zipped=True)
        if target.exists():
            log.info('skipping')
        else:
            log.info('retrieving {0}'.format(self.sql_dump_url))
            urlretrieve(self.sql_dump_url, str(target))
        assert md5(target) == self.sql_dump_md5
        unpacked = target.with_suffix('')
        with gzip.open(str(target)) as f, unpacked.open('wb') as u:
            shutil.copyfileobj(f, u)
        target.unlink()
        log.info('SQL dump for Glottolog release {0} written to {1}'.format(self.version, unpacked))

    def load_sql_dump(self, log):
        dump = self.dump_fname()
        dbname = dump.stem
        db = DB('postgresql://postgres@/{0.stem}'.format(dump))

        if db.exists():
            log.warn('db {0} exists! Drop first to recreate.'.format(dump.stem))
        else:
            if not dump.exists():
                self.download_sql_dump(log)
            db.create()
            subprocess.check_call(['psql', '-d', dbname, '-f', str(dump)])
            log.info('db {0} created'.format(dbname))
