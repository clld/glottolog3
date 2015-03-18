<%inherit file="about_comp.mako"/>

<h3>News</h3>

<h4>Glottolog 2.4</h4>

<dl>
    <dt>References</dt>
    <dd>
        We added references from three new providers:
        <ul>
            <li>68131 references from <a href="/providers/degruyter">De Gruyter language and linguistics books and journals</a></li>
            <li>2144 references from <a href="/providers/goba">Georeferenzierte Online-Bibliographie Areallinguistik</a></li>
            <li>1972 references from <a href="/providers/phoible">The PHOIBLE database bibliography</a></li>
        </ul>
        Thanks for sharing!
    </dd>
    <dt>Languoids</dt>
    <dd>
        76 languages have been added and the classification has been changed (mostly locally), resulting in
        219 new family nodes and 52 updated families.
    </dd>
    <dt>Project Infrastructure</dt>
    <dd>
        The Glottolog data is now curated in a
        ${h.external_link('https://github.com/clld/glottolog-data', label='Git repository hosted at GitHub')}.
        Thus,
        <ul>
        <li>changes to the data in between updates of the Glottolog website are more
        transparent and traceable;</li>
            <li>you can notify us about issues with the data by opening - well -
            ${h.external_link('https://github.com/clld/glottolog-data/issues', label='issues')};</li>
            <li>or even better, you can propose updates to the data using
            ${h.external_link('https://help.github.com/articles/using-pull-requests/', label='pull requests')}.</li>
        </ul>
    </dd>
</dl>


<h4>Glottolog 2.3</h4>

<dl>
    <dt>References</dt>
    <dd>
        While we did remove thousands of obsolete references (duplicates or references that
        have been superseded) 2862 references have also been added and thousands have been
        corrected. When browsing to the URL of one of the obsolete references, you should
        either be redirected (in case of duplicates) with an
        ${h.external_link('http://en.wikipedia.org/wiki/List_of_HTTP_status_codes#301', label="HTTP code of 301")}
        or you should
        see an ${h.external_link('http://en.wikipedia.org/wiki/List_of_HTTP_status_codes#410', label="HTTP 410 Gone")} message.
    </dd>
    <dt>Languoids</dt>
    <dd>
        76 languages have been added and
        classification has been changed (mostly locally), resulting in
        73 new family nodes.
##glottolog3=# select l.id, l.name, ll.hid from language as l, languoid as ll where l.pk = ll.pk and cast(created as date) = '2014-06-25' and ll.level = 'language';
##glottolog3=# select l.id, l.name, ll.hid from language as l, languoid as ll where l.pk = ll.pk and cast(created as date) = '2014-06-25' and ll.level = 'family';
    </dd>
    <dt>Sign Languages</dt>
    <dd>
        Sign Languages have now better coverage and classification. Though the set of
        references, inventory and classification is not yet on the same level as
        for spoken languages.
    </dd>
    <dt>Computerized assignment</dt>
    <dd>
        Many of the relations between references and languages and of the relations between
        references and document types are created by a process
        we call
        <a href="${request.route_url('glossary', _anchor='sec-computerizedassignment')}">computerized assignment</a>.
    </dd>
    <dd>
        Whether relations for a specific reference have been assigned automatically is now
        indicated with small warning signs ${h.icon('warning-sign')}. This information can
        also used for sorting lists of references by clicking the corresponding <strong>ca</strong>
        column head.
    </dd>
    <dd>
        The automatic language guesser has been improved through a better
        training data set, and set to be less aggressive (autoclassifications
        that would make the descriptive status of the language increase are
        blocked). It is still reasonably aggressive however.
    </dd>
</dl>
