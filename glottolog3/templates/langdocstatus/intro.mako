<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>

<%block name="title">GlottoScope</%block>


<%def name="sidebar()">
    <%util:well title="Browse GlottoScope">
        <p>
            <b>GlottoScope</b> provides an interface combining the Endangerment Status
            and Descriptive Status of the languages of the world.
        </p>
        <p>
            Since displaying more than 7000 language locations on a map is rather
            taxing in terms of browser resources, it is advisable to only
            browse by macroarea. If you are confident that your browser has
            enough resources available (in particular enough memory), you may
            choose to view all languages by selecting "World" below.
        </p>
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


<h3>Language Description and Endangerment Status</h3>
<p>

    The <a href="${request.route_url('glossary',
_anchor='sec-descriptivestatusofalanguage')}">descriptive
    status</a> of a language measures how extensive a grammatical
    description there exists for a language. The endangerment status
    measures how endangered the language is according to an
    agglomeration of the databases of
    ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")}
    ,
    ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")}
    and
    ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}.
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
        <th>Glottolog doctypes</th>
        <th># of languages</th>
        <th>% of languages</th>
    </tr>
    </thead>
    <tbody>
        % for sdt, c, a in sdts:
            <tr>
                <th>${sdt.name}</th>
                <td>
                    <ul class="unstyled">
                        % for dt, sdtindex in doctypes:
                            % if sdtindex == sdt.ord or (sdt.name == 'long grammar' and dt.id == 'grammar'):
                                <li>
                                    <a href="${request.route_url('glossary', _anchor='doctype-{0}'.format(dt.id))}">
                                        ${dt}
                                    </a>
                                    % if dt.id == 'grammar':
                                        % if sdt.name == 'long grammar':
                                            with more than 300 pages
                                        % else:
                                            with less than 300 pages
                                        % endif
                                    % endif
                                </li>
                            % endif
                        % endfor
                    </ul>
                </td>
                <td class="right">${c}</td>
                <td class="right">${'{0:.2f}'.format(float(c) * 100 / a)}%</td>
            </tr>
        % endfor
    </tbody>
</table>


