# -*- coding: utf-8 -*-
from collections import defaultdict

from sqlalchemy import not_
import requests
from clld.db.meta import DBSession
from clld.db.models.common import Language_data
from clld.db.util import icontains
from glottolog3.models import Languoid


JSON = 'glottologcurator.json'


def update_lang(lang, **kw):
    """
    store original name in hname

    .. notes::

        We don't update the alternative names (for name search) here, instead, the script
        to update these names in bulk must be run after this function.
    """
    name = kw.pop('name', None)
    if name and name != lang.name:
        if 'hname' not in lang.jsondatadict:
            lang.update_jsondata(hname=lang.name)
        print 'renamed', lang.name, 'to', name
        lang.name = name
        print lang.jsondata

    for k, v in kw.items():
        if k not in lang.datadict():
            DBSession.add(Language_data(key=k, value=v, object_pk=lang.pk))
        else:
            for d in lang.data:
                if d.key == k and d.value != v:
                    print 'updated', k
                    d.value = v
                    break


def download(args):
    #
    # TODO!
    #
    return [
        {
            'action': 'update',
            'id': 'chab1238',
            'name': 'Japhug',
        },
        {
            'action': 'update',
            'id': 'shan1274',
            'name': 'Stodsde',
        },
        {
            'action': 'update',
            'id': 'jiar1239',
            'name': 'Gyalrong',
        },
        {
            'action': 'update',
            'id': 'guan1266',
            'name': 'Khroskyabs',
        },
        {
            'action': 'update',
            'id': 'ribu1240',
            'name': 'Zbu',
            },
        {
            'action': 'update',
            'id': 'caod1238',
            'name': 'Tshobdun',
            },
        {
            'action': 'update',
            'id': 'rgya1239',
            'name': 'Gyalrongic',
            },
        {
            'action': 'update',
            'id': 'daof1238',
            'name': 'Rtau',
        },
        {
            'action': 'update',
            'id': 'kryt1240',
            'name': 'Kryz',
            'name_comment': u'The name form "Kryz" corresponds best to Russian "\u043a\u0440\u044b\u0437\u0441\u043a\u0438\u0439 \u044f\u0437\u044b\u043a", and is used by Authier (2000).',
        },
        {
            'action': 'update',
            'id': 'mana1288',
            'name': 'Manange',
            'name_comment': u'"Manange" is the form of the language name used by Kristine Hildebrandt.',
        },
        {
            'action': 'update',
            'id': 'musk1252',
            'name_pronunciation': u"[m\u0259s'kougi\u0259n] or [m\u0259sko'gi:\u0259n]",
        },
        {
            'action': 'update',
            'id': 'yong1270',
            'speakers': u'40,000 (estimated) (Lidz 2010: 3, based on Yang 2009)',
            'location': u'Yunnan, Sichuan (China)',
        },
        {
            'action': 'update',
            'id': 'avar1256',
            'name': 'Avar',
        },
        {
            'action': 'update',
            'id': 'keoo1238',
            'name': 'Keo',
            'name_comment': u'"Keo" is the name form used by Baird (2008) (in Senft (ed.))',
            },
        {
            'action': 'update',
            'id': 'guan1269',
            'name': 'Kotiria',
            'name_comment': u'According to Stenzel (2013:1), "Wanano" is a name given by unknown outsiders and its use has been called into question by village leaders and the directors, teachers and students of the indigenous school. In 2006, the group publicly adopted the policy of using exclusively their own traditional name Kotiria \'water people\' to refer to themselves and to their language and have requested that the outsiders working with them do the same.',
            },
        {
            'action': 'update',
            'id': 'pira1254',
            'name': "Wa'ikhana",
            'name_comment': u'The Wa\'ikhana have adopted the policy of using the name "Wa\'ikhana" rather than "Piratapuyo".',
        },
        {
            'action': 'update',
            'id': 'mala1533',
            'name': "Malacca-Batavia Creole",
            'name_comment': u'The Portuguese-based creole varieties of Malacca (Malaysia) and Batavia (now Jakarta, Indonesia) are so similar that they are treated as a single language in Glottolog.',
        },
        {
            'action': 'update',
            'id': 'yapu1240',
            'name': "Yeri",
            'name_comment': u'The name "Yeri" is used by Jennifer Wilson (U Buffalo, MPI-EVA Leipzig), actively working on the language (2014).',
        },
        {
            'action': 'update',
            'id': 'araw1276',
            'name': "Lokono",
            'name_comment': u'The name "Lokono" seems to be preferred by linguists working on the language (e.g. Konrad Rybka).',
        },
        {
            'action': 'update',
            'id': 'anyx1238',
            'name': "Anykh",
            'name_comment': u'The name form "Anyx" uses the IPA value of "x".',
        },
        {
            'action': 'update',
            'id': 'kjac1234',
            'name': "Chinese Pidgin Russian",
            'name_comment': u'Chinese Pidgin Russian is also called "Kyakhta Pidgin" because of its prominence in the town of Kyakhta.',
        },
        {
            'action': 'update',
            'id': 'jeri1242',
            'name': "Jeli",
            'name_comment': u'Ethnologue\'s name follows **181522**, but Glottolog adopts the name "Jeli" from **141802**.',
        },
        {
            'action': 'update',
            'id': 'anci1242',
            'name': "Ancient Greek",
            'name_comment': u'This refers to the Greek language in Antiquity and in the Middle Ages, until the end of the Byzantine empire.',
        },
        {
            'action': 'update',
            'id': 'khva1239',
            'name': "Khwarshi",
        },
        {
            'action': 'update',
            'id': 'hinu1240',
            'name': "Hinuq",
            'name_comment': u'The name form "Hinuq" is used by Diana Forker.',
        },
        {
            'action': 'update',
            'id': 'iwai1245',
            'name': "Iwaidjic",
            'name_comment': u'Ethnologue calls the family "Yiwaidjic", but the name of the language is "Iwaidja", so we use "Iwaidjic".',
        },
        {
            'action': 'update',
            'id': 'djam1255',
            'name': "Jaminjung",
            'name_comment': u'Eva Schultze-Berndt uses "Jaminjung".',
        },
        {
            'action': 'update',
            'id': 'djam1254',
            'name': "Jaminjungan",
        },
    ]


def update(args):
    res = defaultdict(lambda: 0)
    for i, spec in enumerate(args.json):
        action = spec.pop('action')
        if action == 'update':
            update_lang(Languoid.get(spec.pop('id')), **spec)
        res[action] += 1

    for k, v in res.items():
        print k, v
