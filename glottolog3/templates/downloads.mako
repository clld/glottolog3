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
            You can download the following files (encoded in UTF-8):
        </p>
        <dl>
            % for model, dls in h.get_downloads(request):
                <dt>${_(model)}</dt>
                % if model == 'Languages':
                <dd>
                    <a href="${request.static_url('glottolog3:static/trees/tree-glottolog-newick.txt')}">
                        Classification as text file in Newick format
                    </a>
                </dd>
                <dd>
                    <a href="${request.route_url('resourcemap', _query=dict(rsc='language'))}">
                        Mapping of Glottocodes to ISO 639-3 codes (and others) in JSON format
                    </a>
                </dd>
                % endif
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
    <%util:well title="Glottolog Data">
        <p>
            The data published by Glottolog is curated in the public GitHub repository
            ${h.external_link("https://github.com/clld/glottolog-data", label='clld/glottolog-data')}.
        </p>
        <p>
            You may report errors you found in Glottolog using this repositories
            ${h.external_link("https://github.com/clld/glottolog-data/issues", label='issue tracker')}.
        </p>
    </%util:well>
</%def>
