<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>

<%block name="title">GlottoScope</%block>

<%def name="browser_link(label, ma, focus)">
    <a class="btn btn-info"
       href="${request.route_url('langdocstatus.browser', _query=dict(macroarea=ma, focus=focus))}"
       title="Go to GlottoScope: A Browser for Language Description and Language Endangerment ${label}">
        <i class="icon-${'heart' if focus == 'ed' else 'book'} icon-white"></i>
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
    ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")},
    ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")} and
    ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}.
</p>

<p>
    <b>GlottoScope</b> provides an interface combining the Endangerment Status
and Descriptive Status of the languages of the world.
</p>
<p>
Since displaying more than 7000 language locations on a map is rather
taxing in terms of browser resources, it is advisable to only
browse by macroarea. If you are confident that your browser has
enough resources available (in particular enough memory), you may
choose to view all languages by selecting "Any" in the macroareas
control of the browser.
</p>

<h4>Browse <b>GlottoScope</b></h4>
<dl>
    % for ma in macroareas:
        <dt>${ma.name}</dt>
        <dd>
            focusing on
            ${browser_link('endangerment', ma.name, 'ed')}
            or
            ${browser_link('focus descriptive status', ma.name, 'sdt')}
        </dd>
    % endfor
    <dt>World</dt>
    <dd>
        focusing on
        ${browser_link('endangerment', '', 'ed')}
        or
        ${browser_link('focus descriptive status', '', 'sdt')}
    </dd>
</dl>