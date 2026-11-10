"""

Create languages-and-dialects-geo.csv download
"""
import shutil
import pathlib
import subprocess
import collections

import transaction
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from csvw.dsv import UnicodeWriter
from clld.db.meta import DBSession
from clld.db.models import common
from clld.cliutil import AppConfig, SessionContext
from clldutils.db import DB
from clldutils.jsonlib import update
from clldutils.path import md5

from glottolog3 import models


def register(parser):
    parser.add_argument('config', action=AppConfig)
    parser.add_argument('out', type=pathlib.Path)


def run(args):  # pragma: no cover
    assert args.out.exists()

    for func, fname in [
        (geo, 'languages_and_dialects_geo.csv'),
        (sqldump, 'glottolog.sql.gz'),
        (newick, 'tree_glottolog_newick.txt'),
    ]:
        fname = args.out / fname
        func(args, fname)
        assert fname.exists()
        args.log.info('%s written', fname)

    register_downloads(args)


def register_downloads(args):
    def bs(p):
        return {
            'bitstreamid': p.name,
            'checksum': md5(p),
            "checksum-algorithm": "MD5",
            "filesize": p.stat().st_size,
        }

    dlfname = args.pkg_dir.joinpath('static', 'downloads.json')
    with update(dlfname, default=collections.OrderedDict(), indent=4, sort_keys=True) as downloads:
        version = args.out.name
        assert version not in downloads
        downloads[version] = dict(
            doi=None, bitstreams=[bs(p) for p in args.out.iterdir()])


def geo(args, fname):
    with SessionContext(args.settings):
        with transaction.manager, UnicodeWriter(fname) as writer:
            writer.writerow([
                'glottocode',
                'name',
                'isocodes',
                'level',
                'macroarea',
                'latitude',
                'longitude'])
            ma_param = common.Parameter.get('macroarea')
            for l in DBSession.query(models.Languoid)\
                    .filter(or_(
                        models.Languoid.level == models.LanguoidLevel.dialect,
                        models.Languoid.level == models.LanguoidLevel.language))\
                    .options(
                        joinedload(common.Language.valuesets)
                            .joinedload(common.ValueSet.values)
                            .joinedload(common.Value.domainelement),
                        joinedload(common.Language.languageidentifier)
                            .joinedload(common.LanguageIdentifier.identifier))\
                    .order_by(common.Language.name):
                macroareas = []
                for vs in l.valuesets:
                    if vs.parameter_pk == ma_param.pk:
                        macroareas = [v.domainelement.name for v in vs.values]
                        break
                writer.writerow([
                    l.id,
                    l.name,
                    ' '.join(
                        i.name for i in l.get_identifier_objs(common.IdentifierType.iso)),
                    l.level,
                    macroareas[0] if macroareas else '',
                    l.latitude if l.latitude is not None else '',
                    l.longitude if l.longitude is not None else ''])


def sqldump(args, fname):
    subprocess.check_call([
        'pg_dump',
        '--no-owner', '--no-privileges',
        '-Z', '9', '-f', str(fname), DB.from_settings(args.settings).name])


def newick(args, fname):
    nodes = collections.OrderedDict((l.id, l) for l in args.repos.languoids())
    trees = []
    for lang in nodes.values():
        if not lang.lineage and (
                lang.id == args.repos.language_types['sign_language'].pseudo_family_id or
                not lang.category.startswith('Pseudo ')):
            ns = lang.newick_node(nodes=nodes).newick
            if lang.level == args.repos.languoid_levels.language and not ns.startswith('('):
                # an isolate without dialects: we wrap it in a pseudo-family with the
                # same name and ID.
                ns = f'({ns}){ns}'
            trees.append(f'{ns};')
    fname.write_text('\n'.join(trees), encoding='utf8')
