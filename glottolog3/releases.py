import gzip
import shutil
import pathlib
import functools
import subprocess
import dataclasses
from urllib.request import urlretrieve

from clldutils.db import DB
from clldutils.path import md5


@functools.total_ordering
@dataclasses.dataclass(frozen=True)
class Release:
    tag: str
    version: str
    sql_dump_md5: str
    downloads_doi: str

    @property
    def version_tuple(self):
        return tuple(map(int, self.version.split('.')))

    def __lt__(self, other):
        return self.version_tuple < other.version_tuple

    def __eq__(self, other):
        return self.version_tuple == other.version_tuple

    @property
    def deposit_id(self):
        return self.downloads_doi.split('zenodo.')[-1]

    @property
    def sql_dump_url(self):
        return f'https://zenodo.org/records/{self.deposit_id}/files/glottolog.sql.gz'

    @classmethod
    def from_downloads(cls, version, spec):
        for bs in spec['bitstreams']:
            if bs['bitstreamid'] == 'glottolog.sql.gz':
                break
        else:
            raise ValueError(version)
        return cls(
            tag='v' + version,
            version=version,
            sql_dump_md5=bs['checksum'],
            downloads_doi=spec['doi'])

    def dump_fname(self, zipped=False):
        return pathlib.Path(f"glottolog-{self.version}.sql{'.gz' if zipped else ''}")

    def download_sql_dump(self, log, out=None):
        target = (out or pathlib.Path('.')) / self.dump_fname(zipped=True)
        unpacked = target.with_suffix('')
        if target.exists() or unpacked.exists():
            log.info('skipping')
            if unpacked.exists():
                return unpacked
        else:
            log.info('retrieving %s', self.sql_dump_url)
            urlretrieve(self.sql_dump_url, str(target))

        assert md5(target) == self.sql_dump_md5
        with gzip.open(str(target)) as f, unpacked.open('wb') as u:
            shutil.copyfileobj(f, u)
        target.unlink()
        log.info('SQL dump for Glottolog release %s written to %s', self.version, unpacked)
        return unpacked

    def load_sql_dump(self, log, out=None):
        dump = self.dump_fname()
        dbname = dump.stem
        db = DB('postgresql://postgres@/{0.stem}'.format(dump))

        if db.exists():
            log.warn('db %s exists! Drop first to recreate.', dump.stem)
        else:
            if not dump.exists():
                unpacked = self.download_sql_dump(log, out=out)
            db.create()
            subprocess.check_call(['psql', '-d', dbname, '-f', str(unpacked)])
            log.info('db %s created', dbname)
