<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="browser_link(label, **query)">
    <a class="label label-info"
       href="${request.route_url('langdocstatus.browser', _query=query)}"
       title="Go to GlottoScope: A Browser for Language Description and Language Endangerment ${label}">
        ${label}
    </a>
</%def>


<h3>Language Description and Endangerment Status</h3>
<p>

    The <a href="${request.route_url('glossary',
    _anchor='sec-descriptivestatusofalanguage')}">descriptive
    status</a> of a language measures how extensive a grammatical
    description there exists for a language. The endangerment status
    measures how endangered the language is according to an
    agglomeration of the databases of
    ${h.external_link("http://www.endangeredlanguages.com", label="The
    Catalogue of Endangered Languages (ELCat)")},
    ${h.external_link("http://www.unesco.org/languages-atlas/",
    label="UNESCO Atlas of the World's Languages in Danger")} and
    ${h.external_link("http://www.ethnologue.com",
    label="Ethnologue")}.

</p>



<p>

GlottoScope provides an interface combining the Endangerment Status
and Descriptive Status of the languages of the world. The underlying
data is drawn from the Glottolog reference collection and Agglomerated
Endangerment information combining endangerment data from the UNESCO
Atlas of the World's Languages, the Catalogue of Endangered Languages
(ELCat) and the latest edition of SIL International's Ethnologue.

Since displaying more than 7000 language locations on a map is rather
taxing in terms of browser resources, it is advisable to only
browse by macroarea. If you are confident that your browser has
enough resources available (in particular enough memory), you may
choose to view all languages by selecting "Any" in the macroareas
control of the browser.

</p>

<h4>Browse status by macro area</h4>
<ul class="inline">
    % for ma in macroareas:
    <li>${browser_link(ma.name, macroarea=ma.name)}</li>
    % endfor
</ul>
<h4>Browse status by language family</h4>
<%util:table items="${families}" args="item" options="${dict(bInfo=True)}" class_="table-nonfluid table-compact">
    <%def name="head()">
        <th>Glottocode</th>
        <th>Name</th>
        <th>Child languages</th>
        <th>Macroareas</th>
    </%def>
    <td>${h.link(request, item, label=item.id)}</td>
    <td>${browser_link(item.name, family=item.id)}</td>
    <td class="right">${item.child_language_count}</td>
    <td>
        <ul class="inline">
            % for ma in item.macroareas:
            <li>${browser_link(ma.name, macroarea=ma.name)}</li>
            % endfor
        </ul>
    </td>
</%util:table>
