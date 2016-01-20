# coding: utf8
from __future__ import unicode_literals
import re

from sqlalchemy import func, select
import transaction
from clld.db.meta import DBSession
from clld.db.models.common import Config, ValueSet

from glottolog3.models import Ref
from glottolog3.scripts.util import get_args


class RedirectMap(dict):
    def get_final(self, key):
        i = 0
        while key in self:
            i += 1
            key = self[key]
            if i > 10:
                raise ValueError(key)
        return key


def main(args):
    source_pattern = re.compile('__Source_(?P<id>[0-9]+)__')
    ref_in_markup_pattern = re.compile('\*\*(?P<id>[0-9]+)\*\*')

    with transaction.manager:
        redirect_map = RedirectMap()
        for key, value in DBSession.query(Config.key, Config.value):
            m = source_pattern.match(key)
            if m and value != '__gone__':
                redirect_map[m.group('id')] = value

        for cfg in DBSession.query(Config)\
                .filter(Config.key.startswith('__Source_'))\
                .filter(Config.value.in_(list(redirect_map.keys()))):
            try:
                new = redirect_map.get_final(cfg.value)
            except ValueError:
                args.log.error('invalid redirect loop: %s' % (cfg.value,))
                new = cfg.value

            if new != cfg.value:
                args.log.info('fixed redirect: %s %s' % (cfg.value, new))
                cfg.value = new

        def repl(m):
            try:
                new = redirect_map.get_final(m.group('id'))
            except ValueError:
                new = m.group('id')
            return '**%s**' % new

        vs_rid = select([
            ValueSet.pk,
            func.unnest(func.regexp_matches(
                ValueSet.description, '\*\*(\d+)\*\*', 'g')).label('ref_id')]).alias()
        for vs in DBSession.query(ValueSet) \
                .filter(ValueSet.pk.in_(
                    DBSession.query(vs_rid.c.pk)
                        .filter(
                            ~DBSession.query(Ref)
                                .filter_by(id=vs_rid.c.ref_id).exists()))) \
                .order_by(ValueSet.id):
            new = ref_in_markup_pattern.sub(repl, vs.description)
            if new != vs.description:
                args.log.info(
                    'fixed obsolete ref id in markup: %s %s' % (vs.description, new))
                vs.description = new


if __name__ == '__main__':  # pragma: no cover
    main(get_args())
