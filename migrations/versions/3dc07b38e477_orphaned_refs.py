# coding=utf-8
"""orphaned refs

Revision ID: 3dc07b38e477
Revises: 42c3ba66574d
Create Date: 2015-04-07 15:07:59.348000

"""

# revision identifiers, used by Alembic.
revision = '3dc07b38e477'
down_revision = '42c3ba66574d'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    isolated = [sa.text('SELECT NOT EXISTS (SELECT 1 FROM %s WHERE EXISTS '
        '(SELECT 1 FROM source WHERE pk = %s.source_pk AND id = :id))' % (tab, tab), conn)
        for tab in ('languagesource', 'valuesetreference')]
    isolated.append(sa.text('SELECT NOT EXISTS (SELECT 1 FROM '
        "(SELECT pk, unnest(regexp_matches(description, '\*\*(\d+)\*\*', 'g')) AS ref_id "
        "FROM valueset WHERE description != '') AS m "
        'WHERE ref_id = :id)', conn))
    unlink = [sa.text('DELETE FROM %s WHERE EXISTS '
        '(SELECT 1 FROM source WHERE pk = %s.ref_pk AND id = :id)' % (tab, tab), conn)
        for tab in ('refcountry', 'refdoctype', 'refmacroarea', 'refprovider')]
    del_ref = sa.text('DELETE FROM ref WHERE EXISTS '
        '(SELECT 1 FROM source WHERE PK = ref.pk AND id = :id)', conn)
    del_source = sa.text('DELETE FROM source WHERE id = :id', conn)
    insert_repl = sa.text('INSERT INTO config (created, updated, active, key, value) '
        'SELECT now(), now(), TRUE, :key, :value '
        'WHERE NOT EXISTS (SELECT 1 FROM config WHERE key = :key)', conn)
    update_trans = sa.text('UPDATE config SET updated = now(), value = :after '
        'WHERE key LIKE :match AND VALUE = :before', conn)

    for id, replacement in ID_REPLACEMENT:
        assert all(i.scalar(id=id) for i in isolated)
        for u in unlink:
            u.execute(id=id)
        del_ref.execute(id=id)
        del_source.execute(id=id)
        if replacement is None:
            replacement = '__gone__'
        insert_repl.execute(key='__Source_%s__' % id, value=replacement)
        update_trans.execute(match='__Source_%__', before=id, after=replacement)


def downgrade():
    pass


ID_REPLACEMENT = [  # 109
    ('7618', '112131'),
    ('7753', '97162'),
    ('8551', None),
    ('9356', '94958'),
    ('13422', '86281'),
    ('15242', '151438'),
    ('17596', '4963'),
    ('29626', '29623'),
    ('30891', None),
    ('36078', '154291'),
    ('44886', None),
    ('47291', '94604'),  #
    ('47609', None),
    ('48898', None),
    ('52234', None),
    ('53198', None),
    ('54087', None),
    ('54650', '103739'),
    ('55898', None),
    ('57468', '321926'),
    ('59671', None),
    ('61716', None),
    ('62428', '14136'),
    ('64293', None),
    ('67547', '45452'),
    ('70589', None),
    ('70890', '105247'),
    ('73206', None),
    ('73397', None),
    ('73771', None),
    ('79745', None),
    ('80665', None),
    ('84226', None),
    ('86223', '163570'),
    ('87897', '126669'),
    ('88123', '29623'),
    ('88158', '18751'),
    ('90793', None),
    ('93831', None),
    ('96692', '326181'),  #
    ('97411', '52509'),
    ('98813', None),
    ('100749', None),
    ('101671', None),
    ('101722', None),
    ('102477', '137946'),
    ('104070', '136620'),
    ('105262', None),
    ('106241', None),
    ('107745', '19774'),
    ('108176', '85819'),
    ('108801', None),
    ('109938', None),
    ('111140', None),
    ('113510', None),
    ('117762', None),
    ('117763', None),
    ('118588', None),
    ('118918', None),
    ('119891', None),
    ('120050', None),
    ('124719', '304184'),
    ('125554', '115363'),
    ('126338', '325970'),
    ('130301', None),
    ('131808', '15260'),  #
    ('132910', None),
    ('134025', '177329'),
    ('134090', None),
    ('134800', '36112'),
    ('137441', None),
    ('138003', None),
    ('141234', None),
    ('142105', None),
    ('142197', '28938'),  #
    ('142916', None),
    ('143297', None),
    ('144326', None),
    ('144368', None),
    ('144812', '184454'),  #
    ('145283', None),
    ('146325', None),
    ('147081', '106031'),
    ('153291', '175234'),
    ('154140', None),
    ('154846', None),
    ('158576', None),
    ('160129', None),
    ('160977', None),
    ('162032', None),
    ('162078', None),
    ('181472', '181284'),
    ('305054', '322840'),
    ('306520', '301189'),
    ('307273', '303769'),
    ('309035', '53178'),
    ('310694', None),
    ('310719', '325155'),  #
    ('310841', '92345'),
    ('311549', '320802'),
    ('312608', '311248'),  #
    ('313936', None),
    ('314001', None),
    ('314386', '161507'),
    ('314691', None),
    ('317374', '104427'),
    ('319057', '326566'),  #
    ('320506', None),
    ('320753', None),
]
