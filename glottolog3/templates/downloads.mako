<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%block name="head">
    <style>
        a.accordion-toggle {font-weight: bold;}
    </style>
</%block>

<h2>Downloads</h2>

<div class="accordion" id="downloads" style="margin-top: 1em; clear: right;">
    <%util:accordion_group eid="acc-current" parent="downloads" title="Current version" open="True">
        <p>
            You can download the following items as zipped, utf-8 encoded archives:
        </p>
        <dl>
            % for model, dls in h.get_downloads(request):
                <dt>${_(model)}</dt>
            % for dl in dls:
                <dd>
                    <a href="${dl.url(request)}">${dl.label(req)}</a>
                </dd>
            % endfor
            % endfor
        </dl>
    </%util:accordion_group>
    % for version, files in reversed(list(u.old_downloads(request))):
    <%util:accordion_group eid="acc-${version.replace('.', '-')}" parent="downloads" title="Version ${version}">
        <ul>
            % for name, url in files:
            <li><a href="${url}">${name}</a></li>
            % endfor
        </ul>
    </%util:accordion_group>
    % endfor
</div>

<%def name="sidebar()">
    <%util:well title="Linked Data">
    <p>
        Glottolog is part of the
        ${h.external_link("http://linguistics.okfn.org/resources/llod/", label='Linguistic Linked Open Data Cloud')}.
        You can request RDF representations of the resources by adding a suitable extension
        (like '.rdf' or '.n3') in the address bar (e.g.
        <a href="${request.route_url('language', id='stan1295', ext='rdf')}">${request.route_url('language', id='stan1295', ext='rdf')}</a>),
        or by using content negotiation. Glottolog makes use of popular ontologies such as Dublin Core.
    </p>
    <p>
        <a href="${request.route_url('glottolog.iso', id='deu')}">${request.route_url('glottolog.iso', id='deu')}</a>
        can be used to link to a language when the ISO 639-3 code is known, but the Glottocode is unknown.
    </p>
    </%util:well>
</%def>
