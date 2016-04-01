# coding: utf8
from __future__ import unicode_literals
import sys
import transaction
import re

from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, joinedload_all
from clldutils.dsv import UnicodeWriter
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language, IdentifierType, LanguageIdentifier

from glottolog3.models import Languoid, LanguoidStatus, LanguoidLevel


def main(args):  # pragma: no cover
    rows = [
        ['glottocode', 'name', 'isocodes', 'level', 'macroarea', 'latitude', 'longitude']]
    version_pattern = re.compile('glottolog\-(?P<version>[0-9]+\.[0-9]+)')

    with transaction.manager:
        # loop over languages and dialects
        for l in DBSession.query(Languoid)\
                .filter(Language.active)\
                .filter(or_(
                    Languoid.level == LanguoidLevel.dialect,
                    and_(
                        Languoid.level == LanguoidLevel.language,
                        Languoid.status == LanguoidStatus.established)))\
                .options(
                    joinedload(Languoid.macroareas),
                    joinedload_all(
                        Language.languageidentifier, LanguageIdentifier.identifier))\
                .order_by(Language.name):
            rows.append([
                l.id,
                l.name,
                ' '.join(i.name for i in l.get_identifier_objs(IdentifierType.iso)),
                l.level,
                l.macroareas[0].name if l.macroareas else '',
                l.latitude if l.latitude is not None else '',
                l.longitude if l.longitude is not None else ''])

    outdir = args.module_dir.joinpath('static', 'download')
    match = version_pattern.search(args.config_uri)
    if match:
        outdir = outdir.joinpath(match.group('version'))
        if not outdir.exists():
            outdir.mkdir()
    with UnicodeWriter(outdir.joinpath('languages-and-dialects-geo.csv')) as writer:
        writer.writerows(rows)


if __name__ == '__main__':
    main(parsed_args())
    sys.exit(0)
