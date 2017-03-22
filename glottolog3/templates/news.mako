<%inherit file="about_comp.mako"/>

<h3>News</h3>

<h4>Glottolog 3.0 - 2017-03-29</h4>

<dl>
    <dt>References</dt>
    <dd>
        <p>
            We added references from a new provider:
        </p>
        <p>
            <a href="${request.route_url('provider', id='benjamins')}">
                Bibliographical records
            </a>
            for all linguistic books and journal articles
            cited in books published by
            ${h.external_link('https://benjamins.com/', label='John Benjamins Publishing Company')}.
        </p>
    </dd>
    <dt>Languoids</dt>
    <dd>
        The language classification has changed in many - smaller and bigger - ways
        since Glottolog 2.7 more than a year ago. We hope to make these changes more
        transparent and tractable by
        ${h.external_link('https://github.com/clld/glottolog', label='using version control for the Glottolog data')}
        and
        ${h.external_link('https://github.com/clld/glottolog/pulls?q=is%3Apr+label%3Aclassification', label='labelling changes to the classification')}
        appropriately.
    </dd>
</dl>

<h4>Glottolog 2.7 - 2016-01-26</h4>

<dl>
    <dt>References</dt>
    <dd>
        <p>
            We added references from a new provider:
        </p>
        <p>
            All
            <a href="${request.route_url('sources', _query=dict(sSearch_8='langsci'))}">
                2802 references
            </a>
            cited in books published by
            ${h.external_link('http://langsci-press.org/', label='Language Science Press')}
            have been added to Glottolog. These references will be curated and added to in the
            future by the Language Science Team.
        </p>
    </dd>
    <dt>Languoids</dt>
    <dd>
        <a href="${request.route_url('languages_alt', ext='atom', _query=dict(type='languages'))}">
            8 languages
        </a>
        have been added and the classification has been changed (mostly locally), resulting in
        <a href="${request.route_url('languages_alt', ext='atom', _query=dict(type='families'))}">
            23 new family nodes
        </a>
        and 7 updated families.
    </dd>
</dl>


<h4>Glottolog 2.6 - 2015-10-07</h4>

<p>
    This edition introduces only minor changes to both, languoids and references. Instead,
    our focus was on improving the release procedures, and in particular aligning data
    curation in ${h.external_link('https://github.com/clld/glottolog-data', label='glottolog-data')}
    and publication at http://glottolog.org. We hope these improvements will allow for more
    frequent updates of the published version of Glottolog in the future.
</p>

<h4>Glottolog 2.5 - 2015-07-17</h4>

<dl>
    <dt>References</dt>
    <dd>
        We added references from three new providers:
        <ul>
            <li>2723 references from the <a href="/providers/bibliolux">Bibliographie zur luxemburgischen Linguistik</a></li>
            <li>1018 references <a href="/providers/gj">collected by Guillaume Jacques</a></li>
            <li>596 references from <a href="/providers/haspelmath">Martin Haspelmath's bibliography</a></li>
        </ul>
        Thanks for sharing!
    </dd>
    <dt>Languoids</dt>
    <dd>
        16 languages have been added and the classification has been changed (mostly locally), resulting in
        53 new family nodes and 15 updated families.
    </dd>
</dl>

<h4>Glottolog 2.4 - 2015-03-20</h4>

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
