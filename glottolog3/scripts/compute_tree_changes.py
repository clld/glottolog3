"""
compare Harald's classification provided as files lff.txt and lof.txt with the current
classification in the glottolog database.

 Binanderean       | 2 bina1276 -> Greater Binanderean
 Morokodo-Beli     | 2 moro1282 -> Baka-Beli
 Mondzish          | 2 mond1268 -> Nuclear Mondzish
 Kowan             | 2 kowa1246 -> Unclassified Madang
 Oirat-Khalkha     | 2 oira1260 -> Eastern Mongolic
 Northern Sangiric | 2 nort2871 -> Sangil-Sangir
 Nuclear Oromo     | 2 nucl1701 -> Oromoid
 Yukpan            | 2 yukp1242 -> Opon-Yukpan
 Tangu-Igom        | 2 tang1354 -> Ataitan
 Jeh-Halang        | 2 jehh1244 -> Kayong-Jeh-Halang
 Etulo-Idoma       | 2 etul1244 -> Akweya
 Munic             | 2 muni1256 -> Munan
 Tamil-Kodagu      | 2 tami1294 -> Tamil-Irula
 Southern Batak    | 2 sout2849 -> Tobaic
 Port Vato-Dakaka  | 2 port1292 -> Orkon-Port Vato-Dakaka
 Western Tucanoan  | 2 west2647 -> Maijiki-Siona
 Angal-Kewa        | 2 anga1291 -> Sau-Angal-Kewa
 Duka              | 2 duka1247 -> Northwestern Kainji
 Kelabitic         | 2 kela1257 -> Dayic
 Hatuhaha          | 2 hatu1244 -> Saparuan
 Dida              | 2 dida1244 -> Neyo-Dida
 Bugis             | 2 bugi1243 -> Tamanic-Bugis
 Chamic            | 2 cham1327 -> Aceh-Chamic
 Coatec            | 2 coat1242 -> Coatlan-Loxicha Zapotec
 Oboloic           | 2 obol1242 -> Lower Cross

"""
from copy import copy
import codecs
import json
import re
from collections import OrderedDict, defaultdict

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.util import nfilter, slug

from glottolog3.lib.bibtex import unescape
from glottolog3.lib.util import glottocode


def data_file(args, name):
    return args.data_file(args.version, name)


NOCODE_PATTERN = re.compile('NOCODE_[\w\-]+$')


def split_families(fp):
    """generator for (node, leafs) pairs parsed from Harald's classification format.
    """
    def normalized_branch(line):
        """parse a line specifying a language family as comma separated list of
        ancestors.
        """
        name_map = {
            'Unclassifiable',  # keep top-level family as subfamily
            'Artificial Language',  # keep top-level family as subfamily
            'Pidgin',  # keep top-level family as subfamily
            'Mixed Language',  # keep top-level family as subfamily
            'Unattested',  # keep top-level family as subfamily
            'Speech Register',  # keep top-level family as subfamily
            'Spurious',  # book keeping 'Preliminary'
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
            family = 'Book keeping'
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
            assert code
            try:
                assert len(code) == 3 or NOCODE_PATTERN.match(code)
            except:
                print code
                raise
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
    """Assemble metadata of a languoid, serializable to JSON.

    :param pk:
    :param level:
    :param kw:
    :return:
    """
    d = dict(pk=pk, level=level, active=True, father_pk=None, status='established')
    d.update(kw)
    return d


def match_nodes(leafs, nodes, rnodes, urnodes, leafsets, names):
    """
    param leafs: set of leafs of a family in the old classification.
    param nodes: list of nodes in the old classification having leafset 'leafs'.
    param rnodes: mapping of tuple of sorted leafs to nodes in the new classification.
    param urnodes: additional mapping for the "unclassified-subtree" case, where two\
    nodes in the new classification may have the same leafset.
    param leafsets: list of sets of leafs for nodes in the new classification ordered by\
    length.
    """
    # first look for exact matches:
    if leafs in rnodes:
        # a node with exactly matching leafset in the new classification exists.
        if leafs in urnodes:
            # actually, more than one!
            # so we make sure there are enough nodes in the old classification, too:
            assert len(nodes) <= 2
            if len(nodes) == 2:
                # determine which corresponds to which by looking at the fathers:
                unode, node = nodes
                if unode[3] != node[0]:
                    node, unode = nodes
                # the "unclassified" node must be a child of the non-unclassified node:
                assert unode[3] == node[0]
                return [
                    Migration(node[0], rnodes[leafs]),
                    Migration(unode[0], urnodes[leafs]),
                ]

        # identify the first node and mark for renaming if more than one node share
        # the same set of leafs.
        todo = [Migration(nodes[0][0], rnodes[leafs], rename=len(nodes) > 1)]

        # mark the others as retired
        for node in nodes[1:]:
            todo.append(Migration(node[0], None, pointer=rnodes[leafs]))
        return todo

    # then look at names:
    #
    # TODO: must look at jsondata['hname']!
    #
    if len(nodes) == 1:
        node = nodes[0]
        if node[2] not in ['Ellicean']:
            # look for the name:
            if node[2] in names and len(names[node[2]]) == 1:
                # unique family name, good enough for a match!
                return [Migration(node[0], names[node[2]][0])]

    # we have to determine a possible counterpart in the new classification by
    # comparing leaf sets and names
    leafset = set(leafs)
    if len(leafs) > 10:
        # comparing leafsets does only make sense for big enough sets
        for nleafset in leafsets:
            # we consider 90% matching leafsets good enough
            allowed_distance = divmod(len(nleafset), 10)[0]
            # first check whether the two sets have roughly the same size:
            if abs(len(leafs) - len(nleafset)) <= allowed_distance:
                # now compute the set differences:
                if (len(leafset - nleafset) <= allowed_distance
                        or len(nleafset - leafset) <= allowed_distance):
                    cp = rnodes[tuple(sorted(list(nleafset)))]
                    return [Migration(node[0], None, pointer=cp) for node in nodes]

    # so far no counterparts found for the leafset under investigation.
    todo = []
    for node in nodes:
        # look for the name:
        if node[2] in names and len(names[node[2]]) == 1:
            # unique family name, good enough for a match!?
            todo.append(Migration(node[0], None, pointer=names[node[2]][0]))
        else:
            mleafset = None
            # look for the smallest leafset in the new classification containing leafset
            for nleafset in leafsets:
                if leafset.issubset(nleafset):
                    mleafset = nleafset
                    break
            if not mleafset:
                # look for the new leafset with the biggest intersection with leafset
                max_intersection = set([])
                for nleafset in leafsets:
                    if len(nleafset.intersection(leafset)) > len(leafset.intersection(max_intersection)):
                        max_intersection = nleafset
                if max_intersection:
                    mleafset = max_intersection
            if not mleafset:
                print '--Missed--', node, leafs
                todo.append(Migration(node[0], None))
            else:
                todo.append(Migration(node[0], None,
                                      pointer=rnodes[tuple(sorted(list(mleafset)))]))
    return todo


def main(args):
    active_only = not args.all
    codes = dict((row[0], row[1]) for row in
                 DBSession.execute("select ll.hid, l.pk from languoid as ll, language as l where ll.pk = l.pk and ll.hid is not null"))

    maxid = DBSession.execute(
        "select pk from languoid order by pk desc limit 1").fetchone()[0]
    gcs = {}

    lnames = {row[0]: row[2] for row in DBSession.execute("select pk, id, name from language")}

    # dict mapping branches (i.e. tuples of sub-family names) to dicts of H-languages
    families = OrderedDict()

    # dict mapping identifiers of H-languages to branches
    languages = OrderedDict()

    parse_families(data_file(args, 'lff.txt'), families, languages)

    # handle isolates / collapse families with exactly one leaf:
    isolate_names = {}
    collapsed_names = {}
    for key in families.keys():
        if len(families[key]) == 1:
            if len(key) == 1:
                # isolate
                languages[families[key].keys()[0]][0] = None
                isolate_names[key[0]] = families[key].keys()[0]  # map name to code
            else:
                languages[families[key].keys()[0]][0] = key[:-1]
                collapsed_names[key[-1]] = families[key].keys()[0]
            del families[key]

    # we also want to be able to lookup families by name
    names = defaultdict(list)
    for branch in families:
        names[branch[-1]].append(branch)

    # now add the unclassifiabble, unattested, un-whatever
    parse_families(data_file(args, 'lof.txt'), families, languages)

    existingnames = lnames.values()
    newlangs = {}
    ncodes = {}
    languoids = []
    for code in languages:
        if code not in codes:
            maxid += 1
            ncodes[code] = maxid
            hnode, status, name = languages[code]
            # we have to insert a new H-language!
            newlangs[name] = (code, name in existingnames)
            attrs = languoid(
                maxid,
                'language',
                hid=code,
                id=glottocode(unicode(name), DBSession, gcs),
                name=name,
                hname=name,
                status=status,
            )
            print '++', attrs
            languoids.append(attrs)

    urnodes = {}
    rnodes = {}
    for family in families:
        #leafs = families[family]
        leafs = tuple(sorted(code for code in families[family].keys() if code in codes))
        try:
            assert leafs
        except:
            print 'Family with only new languages!!'
            print family
            continue
            #raise
        if leafs in rnodes:
            # so we have already seen this exact set of leaves.
            #
            # special case: there may be additional "Unclassified something" nodes in
            # branch without any changes in the set of leafs ...
            try:
                assert [n for n in family if n.startswith('Unclassified')]
            except:
                print family
                print leafs
                # ... or the full leafset contains new languages
                assert [code for code in families[family[:-1]].keys() if code in ncodes]
            fset, rset = set(family), set(rnodes[leafs])
            assert rset.issubset(fset)
            assert leafs not in urnodes
            urnodes[leafs] = family
            #if len(family) > rnodes[leafs]:
            #    rnodes[leafs] = family
        else:
            rnodes[leafs] = family

    #
    # at this point rnodes is a consolidated mapping of sets of H-Languages to branches in
    # the family tree.
    #

    # for set comparisons we compute a list of actual sets of leafs as well
    leafsets = [set(t) for t in sorted(rnodes.keys(), key=lambda s: len(s))]

    todo = []

    # dict mapping (id, name, level) tuples for gl languoids of level family to tuples of leafs
    glnodes = {}
    #
    # note: all languoids with level null have children, thus are not dialects!
    #
    sql = "select l.pk, l.name, ll.level, ll.father_pk from languoid as ll, language as l where ll.pk = l.pk and ll.level = 'family' or ll.level is null"
    if active_only:
        sql = "select l.pk, l.name, ll.level, ll.father_pk from languoid as ll, language as l where ll.pk = l.pk and ll.level = 'family' and l.active = true"

    for row in DBSession.execute(sql).fetchall():
        leafs = [r[0] for r in DBSession.execute(
            "select distinct l.hid from treeclosuretable as t, languoid as l where t.child_pk = l.pk and t.parent_pk = %s and l.hid is not null and l.status != 'provisional'"
            % row[0])]
        if leafs:
            glnodes[(row[0], row[2], row[1], row[3])] = tuple(sorted(leafs))
        else:
            # families without leafs will be marked as retired
            if row[1] in names and len(names[row[1]]) == 1:
                # unique family name, good enough for a match!?
                todo.append(Migration(row[0], None, pointer=names[row[1]][0]))
            else:
                todo.append(Migration(row[0], None))

    # note: for legacy gl nodes, we map leaf-tuples to lists of matching nodes!
    rglnodes = defaultdict(list)
    for node, leafs in glnodes.items():
        rglnodes[leafs].append(node)

    # now we look for matches between old and new classification:
    for leafs, nodes in rglnodes.items():
        assert leafs
        assert nodes
        todo.extend(match_nodes(leafs, nodes, rnodes, urnodes, leafsets, names))

    # compile a mapping for exact matches:
    branch_to_pk = {}
    for m in todo:
        if m.hid:
            if m.hid in branch_to_pk:
                if branch_to_pk[m.hid] != m.pk:
                    # compare names:
                    if lnames[m.pk] == m.hid[-1]:
                        print '#### type1'
                        branch_to_pk[m.hid] = m.pk
                    elif lnames[branch_to_pk[m.hid]] == m.hid[-1]:
                        print '#### type2'
                        pass
                    else:
                        print m.hid
                        print m.hid[-1]
                        print lnames[m.pk]
                        print branch_to_pk[m.hid]
                        print m.pk
                        raise ValueError
            else:
                #assert m.hid not in branch_to_pk
                branch_to_pk[m.hid] = m.pk

    new = 0
    for hnode in sorted(families.keys(), key=lambda b: (len(b), b)):
        # loop through branches breadth first to determine what's to be inserted
        if hnode not in branch_to_pk:
            t = tuple(sorted(families[hnode].keys()))
            if t in rglnodes:
                # the "Unclassified subfamily" special case from above:
                try:
                    assert [n for n in hnode if n.startswith('Unclassified')]
                except:
                    # or the "new language inserted higher up" case!
                    assert [code for code in families[hnode[:-1]].keys() if code in ncodes]
                    #print hnode
                    #print t
                    #raise
                # make sure, the existing glottolog family for the set of leafs is mapped
                # to some other node in the new classification:
                assert rglnodes[t][0][0] in [m.pk for m in todo if m.hid]

            maxid += 1
            attrs = languoid(
                maxid,
                'family',
                id=glottocode(unicode(hnode[-1]), DBSession, gcs),
                name=hnode[-1],
                hname=hnode[-1],
            )
            branch_to_pk[hnode] = maxid
            lnames[maxid] = hnode[-1]
            if len(hnode) > 1:
                attrs['father_pk'] = branch_to_pk[tuple(list(hnode)[:-1])]
                assert attrs['father_pk']
            print '++', attrs
            new += 1
            languoids.append(attrs)

    # now on to the updates for families:
    matches, migrations, nomatches = 0, 0, 0
    for m in todo:
        attrs = languoid(m.pk, 'family', name=lnames[m.pk])
        if m.hid:
            #print '==', lnames[m.pk].encode('utf8'), '->', ', '.join(m.hid).encode('utf8')
            matches += 1

            if len(m.hid) > 1:
                attrs['father_pk'] = branch_to_pk[tuple(list(m.hid)[:-1])]
            if getattr(m, 'rename', False):
                attrs['name'] = m.hid[-1]
            attrs['hname'] = m.hid[-1]
        else:
            attrs['active'] = False
            if getattr(m, 'pointer', False):
                print '~~', lnames[m.pk].encode('utf8'), '->', ', '.join(m.pointer).encode('utf8')
                migrations += 1

                attrs['replacement'] = branch_to_pk[m.pointer]
            else:
                print '--', lnames[m.pk].encode('utf8'), '->'
                nomatches += 1
        languoids.append(attrs)

    print matches, 'matches'
    print migrations, 'migrations'
    print nomatches, 'nomatches'
    print new, 'new nodes'
    print len(newlangs), 'new languages'
    for name, spec in newlangs.items():
        code, exists = spec
        if exists:
            print 'existing name:', name, 'new code:', code

    risolate_names = dict(zip(isolate_names.values(), isolate_names.keys()))
    rcollapsed_names = dict(zip(collapsed_names.values(), collapsed_names.keys()))

    # and updates of father_pks for languages:
    for l in languages:
        hnode, status, name = languages[l]
        id_ = codes.get(l, ncodes.get(l))
        attrs = languoid(id_, 'language', status=status)
        if id_ in lnames and name != lnames[id_]:
            if slug(lnames[id_]) == slug(name):
                attrs['name'] = name
            #else:
            #    print '%s\t%s' % (lnames[id_], name)
        if hnode:
            attrs['father_pk'] = branch_to_pk[hnode]
        # look for hnames!
        if l in risolate_names:
            attrs['hname'] = risolate_names[l]
        if l in rcollapsed_names:
            attrs['hname'] = rcollapsed_names[l]
        languoids.append(attrs)

    for row in DBSession.execute(
        "select l.pk, ll.hid, l.name from languoid as ll, language as l where ll.pk = l.pk and ll.hid like '%NOCODE_%'"
    ).fetchall():
        if row[1] not in languages:
            # languoids with Harald's private code that are no longer in use
            attrs = languoid(
                row[0], 'language', status='retired', active=False, father_pk=None)
            languoids.append(attrs)

    with open(data_file(args, 'languoids.json'), 'w') as fp:
        json.dump(languoids, fp)


if __name__ == '__main__':
    main(parsed_args(
        (("--all",), dict(action="store_true")),
        (("--version",), dict(default="")),
    ))
