<%inherit file="about_comp.mako"/>

<h3>News</h3>

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
