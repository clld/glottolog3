import gzip
import shutil
import pathlib
import subprocess
import dataclasses
from urllib.request import urlretrieve

from clldutils.db import DB
from clldutils.path import md5


@dataclasses.dataclass(frozen=True)
class Release:
    tag: str
    version: str
    sql_dump_md5: str
    downloads_doi: str

    @property
    def deposit_id(self):
        return self.downloads_doi.split('zenodo.')[-1]

    @property
    def sql_dump_url(self):
        return f'https://zenodo.org/records/{self.deposit_id}/files/glottolog.sql.gz'

    @classmethod
    def from_config(cls, cfg, section):
        try:
            return cls(
            tag=section,
            version=cfg[section]['version'],
            sql_dump_md5=cfg[section]['sql_dump_md5'],
            downloads_doi=cfg[section]['doi'])
        except KeyError:
            print(cfg[section])

    def dump_fname(self, zipped=False):
        return pathlib.Path(f"glottolog-{self.version}.sql{'.gz' if zipped else ''}")

    def download_sql_dump(self, log):
        target = self.dump_fname(zipped=True)
        if target.exists():
            log.info('skipping')
        else:
            log.info('retrieving %s', self.sql_dump_url)
            urlretrieve(self.sql_dump_url, str(target))
        assert md5(target) == self.sql_dump_md5
        unpacked = target.with_suffix('')
        with gzip.open(str(target)) as f, unpacked.open('wb') as u:
            shutil.copyfileobj(f, u)
        target.unlink()
        log.info('SQL dump for Glottolog release %s written to %s', self.version, unpacked)

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
