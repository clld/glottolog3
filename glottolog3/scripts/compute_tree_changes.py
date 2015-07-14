"""
compare Harald's classification provided as files lff.txt and lof.txt with the current
classification in the glottolog database.

input:
- glottolog-data/languoids/lff.txt
- glottolog-data/languoids/lof.txt

output:
- glottolog-data/languoids/changes.json
"""
from copy import copy
import codecs
import re
from collections import OrderedDict, defaultdict, Counter, namedtuple

from sqlalchemy.sql import select, and_

from clld.db.meta import DBSession
from clld.db.models.common import Language
from clld.util import nfilter, slug, jsondump

from glottolog3.models import (
    BOOKKEEPING, Languoid, LanguoidLevel, TreeClosureTable, LanguoidStatus,
)
from glottolog3.lib.bibtex import unescape
from glottolog3.lib.util import glottocode
from glottolog3.scripts.util import get_args


NOCODE_PATTERN = re.compile('NOCODE_[\w\-]+$')
GLNode = namedtuple('GLNode', 'pk name level father_pk hname')


def get_leafset(iterable):
    return tuple(sorted(list(iterable)))


def split_families(fp):
    """generator for (node, leafs) pairs parsed from Harald's classification format.
    """
    def normalized_branch(line):
        """parse a line specifying a language family as comma separated list of
        ancestors.
        """
        name_map = {
            'Unattested',  # keep top-level family as subfamily
            'Unclassifiable',  # keep top-level family as subfamily
            'Pidgin',  # keep top-level family as subfamily
            'Mixed Language',  # keep top-level family as subfamily
            'Artificial Language',  # keep top-level family as subfamily
            'Speech Register',  # keep top-level family as subfamily
            # FIXME: also 'Sign Language'?
            'Spurious',  # bookkeeping 'Preliminary'
        }
        branch = [unescape(n.strip().replace('_', ' ')) for n in line.split(',')]
        if branch[0] not in name_map:
            return branch, 'established'
        family = branch.pop(0)
        subfamily = None
        retired = False
        if branch:
            # there's a second level!
            if family == 'Spurious':
                if branch[0] == 'Retired':
                    retired = True
                    branch.pop(0)
            else:
                subfamily = '%s (%s)' % (branch.pop(0), family)
        status = 'established'
        if family in ['Spurious', 'Unattested']:
            status = family.lower()
            if retired:
                status += ' retired'
        if family == 'Spurious':
            family = BOOKKEEPING
        return nfilter([family, subfamily]), status

    family = None
    for line in fp.read().split('\n'):
        if not line.strip():
            continue
        if line.strip().endswith('TODO'):
            print 'ignoring:', line
            continue
        if line.startswith('  '):
            name, code = line.strip().split('[')
            code = code.split(']')[0].replace('\\', '').replace('"', '').replace("'", '')
            code = code.replace('NOCODE-', 'NOCODE_')
            try:
                assert len(code) == 3 or NOCODE_PATTERN.match(code)
            except:
                raise ValueError(code)
            family[1][code] = unescape(name.strip().replace('_', ' '))
        else:
            if family:
                yield family
            family = [normalized_branch(line), {}]
    yield family


def parse_families(filename, families, languages):
    """reads filename, appends parsed data to families and languages.
    """
    with codecs.open(filename, encoding='utf8') as fp:
        for (branch, status), leafs in split_families(fp):
            for code, name in leafs.items():
                # record where in the tree a language is attached
                languages[code] = [tuple(branch), status, name]

            for i in range(len(branch)):
                p = tuple(branch[:i + 1])
                if p in families:
                    families[p].update(leafs)
                else:
                    families[p] = copy(leafs)


class Migration(object):
    """Object to store information about a migration, i.e. a change of a languoid.
    """
    def __init__(self, pk, hid, **kw):
        """
        pk: primary key of the languoid affected.
        hid:
        """
        self.pk = pk
        self.hid = hid
        for k, v in kw.items():
            setattr(self, k, v)


def languoid(pk, level, **kw):
    """Assemble metadata of a languoid, serializable to JSON."""
    d = dict(pk=pk, level=level, active=True, father_pk=None, status='established')
    d.update(kw)
    return d


def match_nodes(args,
                gl_leafset,
                gl_nodes,
                hh_leafset_to_branch,
                hh_duplicate_leafset_to_branch,
                hh_leafsets,
                name_to_branches):
    """
    param gl_leafs: set of leafs of a family in the old classification.
    param gl_nodes: list of nodes in the old classification having leafset 'gl_leafs'.
    param hh_leafset_to_branch: mapping of tuple of sorted leafs to nodes in the new \
    classification.
    param hh_duplicate_leafset_to_branch: additional mapping for the \
    "unclassified-subtree" case, where two nodes in the new classification may have the \
    same leafset.
    param hh_leafsets: list of sets of leafs for nodes in the new classification ordered\
    by length.
    """
    # first look for exact matches:
    # 0 = pk, 1 = level, 2 = name, 3 = father_pk
    if gl_leafset in hh_leafset_to_branch:
        # a node with exactly matching leafset in the new classification exists.
        if gl_leafset in hh_duplicate_leafset_to_branch:
            # actually, more than one!
            # so we make sure there are enough nodes in the old classification, too:
            assert len(gl_nodes) <= 2
            if len(gl_nodes) == 2:
                # determine which corresponds to which by looking at the fathers:
                unode, node = gl_nodes
                if unode.father_pk != node.pk:
                    node, unode = gl_nodes
                # the "unclassified" node must be a child of the non-unclassified node:
                assert unode.father_pk == node.pk
                return [
                    Migration(node.pk, hh_leafset_to_branch[gl_leafset]),
                    Migration(unode.pk, hh_duplicate_leafset_to_branch[gl_leafset]),
                ]

        # identify the first node and mark for renaming if more than one node share
        # the same set of leafs.
        todo = [Migration(
            gl_nodes[0].pk, hh_leafset_to_branch[gl_leafset], rename=len(gl_nodes) > 1)]

        # mark the others as retired
        for node in gl_nodes[1:]:
            todo.append(
                Migration(node[0], None, pointer=hh_leafset_to_branch[gl_leafset]))
        return todo

    # then look at name_to_branches:
    if len(gl_nodes) == 1:
        node = gl_nodes[0]
        if node.name not in ['Ellicean']:
            # look for the name:
            for attr in ['name', 'hname']:
                name = getattr(node, attr)
                if name in name_to_branches and len(name_to_branches[name]) == 1:
                    # unique family name, good enough for a match!
                    return [Migration(node.pk, name_to_branches[name][0])]

    # we have to determine a possible counterpart in the new classification by
    # comparing leaf sets and name_to_branches
    leafset = set(gl_leafset)
    if len(gl_leafset) > 10:
        # comparing hh_leafsets does only make sense for big enough sets
        for nleafset in hh_leafsets:
            # we consider 90% matching hh_leafsets good enough
            allowed_distance = divmod(len(nleafset), 10)[0]
            # first check whether the two sets have roughly the same size:
            if abs(len(gl_leafset) - len(nleafset)) <= allowed_distance:
                # now compute the set differences:
                if (len(leafset - nleafset) <= allowed_distance
                        or len(nleafset - leafset) <= allowed_distance):
                    cp = hh_leafset_to_branch[tuple(sorted(list(nleafset)))]
                    return [Migration(node.pk, None, pointer=cp) for node in gl_nodes]

    # so far no counterparts found for the leafset under investigation.
    todo = []
    for node in gl_nodes:
        # look for the name:
        for attr in ['name', 'hname']:
            name = getattr(node, attr)
            if name in name_to_branches and len(name_to_branches[name]) == 1:
                # unique family name, good enough for a match!?
                todo.append(Migration(node.pk, None, pointer=name_to_branches[name][0]))
                break
        else:
            mleafset = None
            # look for the smallest leafset in the new classification containing leafset
            for nleafset in hh_leafsets:
                if leafset.issubset(nleafset):
                    mleafset = nleafset
                    break
            if not mleafset:
                # look for the new leafset with the biggest intersection with leafset
                max_intersection = set([])
                for nleafset in hh_leafsets:
                    if len(nleafset.intersection(leafset)) > len(
                            leafset.intersection(max_intersection)):
                        max_intersection = nleafset
                if max_intersection:
                    mleafset = max_intersection
            if not mleafset:
                args.log.warn('--Missed-- %s %s' % (node, gl_leafset))
                todo.append(Migration(node[0], None))
            else:
                todo.append(Migration(
                    node[0], None,
                    pointer=hh_leafset_to_branch[get_leafset(mleafset)]))
    return todo


def main(args):
    stats = Counter(new=0, matches=0, migrations=0, nomatches=0)
    l, ll = Language.__table__.alias('l'), Languoid.__table__.alias('ll')
    gl_languoids = list(DBSession.execute(
        select([l, ll], use_labels=True).where(l.c.pk == ll.c.pk)).fetchall())

    # we collect a list of changes which we will store in a JSON file.
    changes = []

    hid_to_pk = {row['ll_hid']: row['l_pk'] for row in gl_languoids if row['ll_hid']}
    max_languoid_pk = max(*[row['l_pk'] for row in gl_languoids])
    new_glottocodes = {}
    pk_to_name = {row['l_pk']: row['l_name'] for row in gl_languoids}

    # dict mapping branches (i.e. tuples of sub-family names) to dicts of H-languages
    hh_families = OrderedDict()

    # dict mapping identifiers (i.e. hid) of H-languages to branches
    hh_languages = OrderedDict()

    parse_families(
        args.data_dir.joinpath('languoids', 'lff.txt'), hh_families, hh_languages)

    # handle isolates / collapse families with exactly one leaf:
    isolate_names = {}
    collapsed_names = {}
    for key in hh_families.keys():
        if len(hh_families[key]) == 1:
            if len(key) == 1:
                # isolate
                hh_languages[hh_families[key].keys()[0]][0] = None
                isolate_names[key[0]] = hh_families[key].keys()[0]  # map name to code
            else:
                hh_languages[hh_families[key].keys()[0]][0] = key[:-1]
                collapsed_names[key[-1]] = hh_families[key].keys()[0]
            del hh_families[key]

    # now add the unclassifiabble, unattested, un-whatever
    parse_families(
        args.data_dir.joinpath('languoids', 'lof.txt'), hh_families, hh_languages)

    # we also want to be able to lookup families by name
    fname_to_branches = defaultdict(list)
    for branch in hh_families:
        fname_to_branches[branch[-1]].append(branch)

    new_hid_to_pk = {}
    for code, (hnode, status, name) in hh_languages.items():
        if code not in hid_to_pk:
            # we have to insert a new H-language!
            max_languoid_pk += 1
            new_hid_to_pk[code] = max_languoid_pk
            if name in pk_to_name.values():
                args.log.warn('new code {1} for existing name {0}'.format(name, code))
            changes.append(languoid(
                max_languoid_pk,
                'language',
                hid=code,
                id=glottocode(unicode(name), DBSession, new_glottocodes),
                name=name,
                hname=name,
                status=status))
            stats.update(['new_languages'])

    duplicate_leafset_to_branch = {}
    leafset_to_branch = {}
    for family, langs in hh_families.items():
        leafs = get_leafset(hid for hid in langs.keys() if hid in hid_to_pk)
        if not leafs:
            args.log.info('Family with only new languages: %s, %s' % (family, langs))
            continue

        if leafs in leafset_to_branch:
            # so we have already seen this exact set of leaves.
            #
            # special case: there may be additional "Unclassified something" nodes in
            # branch without any changes in the set of leafs ...
            if not [n for n in family if n.startswith('Unclassified')]:
                # ... or the full leafset contains new languages
                assert [hid for hid in hh_families[family[:-1]].keys()
                        if hid in new_hid_to_pk]
            fset, rset = set(family), set(leafset_to_branch[leafs])
            assert rset.issubset(fset)
            assert leafs not in duplicate_leafset_to_branch
            duplicate_leafset_to_branch[leafs] = family
        else:
            leafset_to_branch[leafs] = family

    #
    # at this point leafset_to_branch is a consolidated mapping of sets of H-Languages
    # to branches in the new family tree.
    #

    # for set comparisons we compute a list of actual sets (not tuples) of leafs
    # ordered by length.
    leafsets = [set(t) for t in sorted(leafset_to_branch.keys(), key=lambda s: len(s))]

    todo = []

    gl_family_to_leafset = {}

    def select_leafs(pk):
        l, tc = Languoid.__table__.alias('l'), TreeClosureTable.__table__.alias('tc')
        return [r['l_hid'] for r in DBSession.execute(
            select([l, tc], use_labels=True).where(and_(
                l.c.pk == tc.c.child_pk,
                l.c.hid != None,
                l.c.status != LanguoidStatus.provisional,
                tc.c.parent_pk == pk)))]

    for row in gl_languoids:
        if row['ll_level'] == LanguoidLevel.family and row['l_active']:
            leafs = get_leafset(select_leafs(row['l_pk']))
            assert leafs
            glnode = GLNode(
                row['l_pk'],
                row['l_name'],
                row['ll_level'].name,
                row['ll_father_pk'],
                row['l_jsondata'].get('hname'))
            gl_family_to_leafset[glnode] = leafs

    # note: for legacy gl nodes, we map leaf-tuples to lists of matching nodes!
    leafset_to_gl_family = defaultdict(list)
    for node, leafs in gl_family_to_leafset.items():
        leafset_to_gl_family[leafs].append(node)

    # now we look for matches between old and new classification:
    for leafs, nodes in leafset_to_gl_family.items():
        todo.extend(match_nodes(
            args,
            leafs,
            nodes,
            leafset_to_branch,
            duplicate_leafset_to_branch,
            leafsets,
            fname_to_branches))

    # compile a mapping for exact matches:
    branch_to_pk = {}
    for m in todo:
        if m.hid:
            if m.hid in branch_to_pk:
                if branch_to_pk[m.hid] != m.pk:
                    # compare names:
                    if pk_to_name[m.pk] == m.hid[-1]:
                        args.log.info('#### type1')
                        branch_to_pk[m.hid] = m.pk
                    elif pk_to_name[branch_to_pk[m.hid]] == m.hid[-1]:
                        args.log.info('#### type2')
                    else:
                        raise ValueError
            else:
                branch_to_pk[m.hid] = m.pk

    for hnode in sorted(hh_families.keys(), key=lambda b: (len(b), b)):
        # loop through branches breadth first to determine what's to be inserted
        if hnode not in branch_to_pk:
            t = get_leafset(hh_families[hnode].keys())
            if t in leafset_to_gl_family:
                # the "Unclassified subfamily" special case from above:
                if not [n for n in hnode if n.startswith('Unclassified')]:
                    assert [hid for hid in hh_families[hnode[:-1]].keys()
                            if hid in new_hid_to_pk]
                # make sure, the existing glottolog family for the set of leafs is mapped
                # to some other node in the new classification:
                assert leafset_to_gl_family[t][0].pk in [m.pk for m in todo if m.hid]

            max_languoid_pk += 1
            branch_to_pk[hnode] = max_languoid_pk
            pk_to_name[max_languoid_pk] = hnode[-1]
            attrs = languoid(
                max_languoid_pk,
                'family',
                id=glottocode(unicode(hnode[-1]), DBSession, new_glottocodes),
                name=hnode[-1],
                hname=hnode[-1],
            )
            if len(hnode) > 1:
                attrs['father_pk'] = branch_to_pk[tuple(list(hnode)[:-1])]
                assert attrs['father_pk']
            stats.update(['new'])
            changes.append(attrs)

    # now on to the updates for families:
    for m in todo:
        attrs = languoid(m.pk, 'family', name=pk_to_name[m.pk])
        if m.hid:
            stats.update(['matches'])
            if len(m.hid) > 1:
                attrs['father_pk'] = branch_to_pk[tuple(list(m.hid)[:-1])]
            if getattr(m, 'rename', False):
                attrs['name'] = m.hid[-1]
            attrs['hname'] = m.hid[-1]
        else:
            attrs['active'] = False  # mark the languoid as obsolete.
            if getattr(m, 'pointer', False):
                print '~~', m.pk, pk_to_name[m.pk].encode('utf8'), '->', \
                    ', '.join(m.pointer).encode('utf8')
                stats.update(['migrations'])
                attrs['replacement'] = branch_to_pk[m.pointer]
            else:
                stats.update(['nomatches'])
        changes.append(attrs)

    args.log.info('%s' % stats)

    risolate_names = dict(zip(isolate_names.values(), isolate_names.keys()))
    rcollapsed_names = dict(zip(collapsed_names.values(), collapsed_names.keys()))

    # and updates of father_pks for languages:
    for l, (hnode, status, name) in hh_languages.items():
        id_ = hid_to_pk.get(l, new_hid_to_pk.get(l))
        attrs = languoid(id_, 'language', status=status)
        if id_ in pk_to_name and name != pk_to_name[id_]:
            if slug(pk_to_name[id_]) == slug(name):
                attrs['name'] = name
        if hnode:
            attrs['father_pk'] = branch_to_pk[hnode]
        # look for hnames!
        if l in risolate_names:
            attrs['hname'] = risolate_names[l]
        if l in rcollapsed_names:
            attrs['hname'] = rcollapsed_names[l]
        changes.append(attrs)

    for row in gl_languoids:
        hid = row['ll_hid']
        if hid and 'NOCODE' in hid and hid not in hh_languages:
            # languoids with Harald's private code that are no longer in use
            changes.append(languoid(
                row['l_pk'], 'language', status='retired', active=False, father_pk=None))

    jsondump(changes, args.data_dir.joinpath('languoids', 'changes.json'), indent=4)


if __name__ == '__main__':
    main(get_args())
