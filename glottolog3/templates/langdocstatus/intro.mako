<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "glottoscope" %>

<%block name="title">GlottoScope</%block>


<%def name="sidebar()">
    <%util:well>
        <div class="alert alert-info smaller">
            Since displaying more than 7000 languages on a map is rather
            taxing for the browser, it is advisable to only
            browse by macroarea.
        </div>
        <table class="table table-nonfluid table-condensed">
            <thead>
            <tr>
                <th>Macroarea</th>
                <th colspan="2" style="text-align: center">focus</th>
            </tr>
            </thead>
            <tbody>
                % for ma in macroareas:
                    <tr>
                        <th>${ma.name}</th>
                        <td>
                            ${browser_link('endangerment', ma.name, 'ed')}
                        </td>
                        <td>
                            ${browser_link('descriptive status', ma.name, 'sdt')}
                        </td>
                    </tr>
                % endfor
            <tr>
                <th>World</th>
                <td>
                    ${browser_link('endangerment', '', 'ed')}
                </td>
                <td>
                    ${browser_link('descriptive status', '', 'sdt')}
                </td>
            </tr>
            </tbody>
        </table>
    </%util:well>
</%def>



<%def name="browser_link(label, ma, focus)">
    <a class="btn btn-info"
       href="${request.route_url('langdocstatus.browser', _query=dict(macroarea=ma, focus=focus))}"
       title="Go to GlottoScope: A Browser for Language Description and Language Endangerment ${label}">
        <i class="icon-${'heart' if focus == 'ed' else 'book'} icon-white"></i>
        ${label}
    </a>
</%def>


<h3>GlottoScope</h3>
<p>
    <b>GlottoScope</b> provides a visualisation of the combination of
    <b>${aes.name} (${aes.id.upper()})</b>
    and <b>${med.name}</b> of the languages of the world (but since descriptive status
    can only be reliably computed from Glottolog data for spoken L1 languages and sign
    languages, we only display these).
</p>

<p>
    GlottoScope was designed and developed by Robert Forkel and Harald Hammarström in 2014.
    Comments and beta-testing were provided by a number of individuals
    including Hedvig Skirgård, Martin Haspelmath, Matti Miestamo, Mark
    Dingemanse, Lyle Campbell, Tapani Salminen and audiences at several
    demo sessions.
</p>

<p>
    For more information see ${h.link(req, ref)}.
</p>

<h4>Agglomerated Endangerment Status</h4>
<p>
    The Agglomerated Endangerment Status measures how endangered a language is. Originally, most of the
    endangerment assessments were aggregated from
    ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")}
    ,
    ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")}
    and
    ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}.
    Over time, assessments from other sources were included as well. For a full list of sources, see
    ${h.external_link("https://github.com/glottolog/glottolog/blob/master/config/aes_sources.ini", label="AES sources in the Glottolog repository")].
</p>
<table class="table table-nonfluid">
    <thead>
    <tr>
        <th>AES status</th>
        <th># of languages</th>
        <th>% of languages</th>
    </tr>
    </thead>
    <tbody>
        % for de in aes.domain:
            <tr>
                <th>${de.name}</th>
                <td class="right">${aes_status_count[de.pk]}</td>
                <td class="right">${'{0:.2f}'.format(float(aes_status_count[de.pk]) * 100 / sum(aes_status_count.values()))}%</td>
            </tr>
        % endfor
    <tr><th>total:</th><td class="right">${sum(aes_status_count.values())}</td><td> </td></tr>
    </tbody>
</table>


<h4>Descriptive Status</h4>
<p>
    The <a href="${request.route_url('glossary',
_anchor='sec-descriptivestatusofalanguage')}">descriptive
    status</a> of a language measures how extensive a grammatical
    description there exists for a language.
</p>

<p>
    For the purpose of the descriptive status Glottolog's regular document types are
    mapped
    a more coarse grained <b>M</b>ost <b>E</b>xtensive <b>Description</b> (MED) type as
    follows:
</p>

<table class="table table-nonfluid">
    <thead>
    <tr>
        <th>MED type</th>
        <th>Description</th>
        <th># of languages</th>
        <th>% of languages</th>
    </tr>
    </thead>
    <tbody>
        % for de in med.domain:
            <tr>
                <th>${de.name}</th>
                <td>${de.description}</td>
                <td class="right">${med_type_count[de.pk]}</td>
                <td class="right">${'{0:.2f}'.format(float(med_type_count[de.pk]) * 100 / sum(med_type_count.values()))}%</td>
            </tr>
        % endfor
    <tr><th>total:</th><td> </td><td class="right">${sum(med_type_count.values())}</td><td> </td></tr>
    </tbody>
</table>
