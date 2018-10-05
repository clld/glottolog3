<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>

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
    <b>Agglomerated Endangerment Status (AES)</b>
    and <b>Descriptive Status</b> of the languages of the world.
</p>

<p>
    GlottoScope was designed and developed by Robert Forkel and Harald Hammarström in 2014.
    Comments and beta-testing were provided by a number of individuals
    including Hedvig Skirgård, Martin Haspelmath, Matti Miestamo, Mark
    Dingemanse, Lyle Campbell, Tapani Salminen and audiences at several
    demo sessions.
</p>

<p>
    For more information see:
</p>
<blockquote>
    Harald Hammarström and Thom Castermans and Robert Forkel and Kevin Verbeek and Michel A. Westenberg and Bettina Speckmann.
    2018. Simultaneous Visualization of Language Endangerment and Language Description.
    <i>Language Documentation & Conservation</i>, 12, 359-392.<br>
    ${h.external_link('http://hdl.handle.net/10125/24792')}
</blockquote>

<h4>Agglomerated Endangerment Status</h4>
<p>
    The Agglomerated Endangerment Status measures how endangered a language is according to an
    agglomeration of the databases of
    ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")}
    ,
    ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")}
    and
    ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}.
</p>


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
