"""
Create languages-and-dialects-geo.csv download
"""
import transaction
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from csvw.dsv import UnicodeWriter
from clld.db.meta import DBSession
from clld.db.models import common
from clld.cliutil import AppConfig, SessionContext

from glottolog3 import models


def register(parser):
    parser.add_argument('config', action=AppConfig)


def run(args):  # pragma: no cover
    with SessionContext(args.settings):
        fname = args.pkg_dir.joinpath('static', 'download', 'languages-and-dialects-geo.csv')
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

        args.log.info('{0} written'.format(fname))
