"""
noderefs.json
    {
        "languoidbase::id": 104384,
        "languoidbase_id": 104384,
        "record_creation_date": "07/10/2012",
        "record_creator_account": "HASPELMATH",
        "record_modification_date": "11/04/2013",
        "record_modifier_account": "Benedikt",
        "refbase::id": 9853,
        "refbase_id": 9853
    },
noderefs_deleted.json
    {
        "languoidbase_id": 36667,
        "record_creation_date": "09/19/2013",
        "record_creator_account": "Nico",
        "refbase_id": 43851
    },
"""
import json
from collections import defaultdict

from sqlalchemy import create_engine


def get_recs(name):
    with open(name + '.json') as fp:
        recs = json.load(fp)
    return recs


def language_pk(superseded, rec):
    pk = rec['languoidbase_id']
    while pk in superseded:
        pk = superseded[pk]
    return pk


def main():
    conn = create_engine('postgresql://robert@/glottolog3')
    superseded = {r[0]: r[1] for r in conn.execute("select languoid_pk, replacement_pk from superseded")}

    create = defaultdict(list)
    delete = defaultdict(list)

    for rec in get_recs('noderefs'):
        if rec['record_creator_account']:
            create[rec['refbase_id']].append(language_pk(superseded, rec))

    for rec in get_recs('noderefs_deleted'):
        delete[rec['refbase_id']].append(language_pk(superseded, rec))

    with open('../brugmann_noderefs.json', 'w') as fp:
        json.dump(dict(create=create, delete=delete), fp)


if __name__ == '__main__':
    main()
