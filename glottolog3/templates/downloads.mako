<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%block name="head">
    <style>
        a.accordion-toggle {font-weight: bold;}
    </style>
</%block>

<h2>Downloads</h2>

<div class="alert alert-info">
    <p>
        The data served by <a href="https://glottolog.org">glottolog.org</a> including the downloads
        linked below is created from the data curated in the GitHub repository
        ${h.external_link("https://github.com/clld/glottolog", label='clld/glottolog')}.
    </p>
    <p>
        ${h.external_link("https://github.com/clld/glottolog/releases", label="Releases")}
        of this repository are archived with and retrievable from ZENODO at
    </p>
    <p>
        <strong>${h.external_link("https://doi.org/10.5281/zenodo.596479", label="DOI: 10.5281/zenodo.596479")}</strong>
    </p>
</div>

<div class="accordion" id="downloads" style="margin-top: 1em; clear: right;">
    % for version, links in reversed(list(u.old_downloads())):
        % if loop.first:
            <%util:accordion_group eid="acc-${version.replace('.', '-')}" parent="downloads" title="Version ${version}" open="True">
                <ul>
                    % for link in links:
                        <li>${link|n}</li>
                    % endfor
                </ul>
            </%util:accordion_group>
        % else:
            <%util:accordion_group eid="acc-${version.replace('.', '-')}" parent="downloads" title="Version ${version}">
                <ul>
                    % for link in links:
                        <li>${link|n}</li>
                    % endfor
                </ul>
            </%util:accordion_group>
        % endif
    % endfor
</div>

<%def name="sidebar()">
    <%util:well title="Download Files">
        <dl>
            <dt>glottolog.sql.gz</dt>
            <dd>gzipped PostgreSQL 9.x database dump</dd>
            <dt>glottolog_languoid.csv.zip</dt>
            <dd>tabular description of Glottolog languoids, one row per languoid, in (zipped) CSV</dd>
            <dt>glottolog_source.bib.zip</dt>
            <dd>zipped BibTeX file containing all Glottolog references</dd>
            <dt>languages_and_dialects_geo.csv</dt>
            <dd>CSV file containing geographic locations for Glottolog languages and dialects</dd>
            <dt>tree_glottolog_newick.txt</dt>
            <dd>Trees for all Glottolog top-level families encoded in Newick format</dd>
        </dl>
    </%util:well>
    <%util:well title="Glottolog Data">
        <p>
            The data published by Glottolog is curated in the public GitHub repository
            ${h.external_link("https://github.com/clld/glottolog", label='clld/glottolog')}.
        </p>
        <p>
            You may report errors you found in Glottolog using this repositories
            ${h.external_link("https://github.com/clld/glottolog/issues", label='issue tracker')}.
        </p>
    </%util:well>
</%def>
