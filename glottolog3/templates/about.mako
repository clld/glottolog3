<%inherit file="about_comp.mako"/>
<%namespace name="util" file="util.mako"/>


<h3>About Glottolog</h3>

<ul class="nav nav-pills">
    % for label in 'Credits Contributing Publications'.split():
        <li class="active">
            <a href="#${label.lower()}">${label}</a>
        </li>
    % endfor
</ul>

<%util:section title="Credits" level="3" id="credits">
        <p>
            Glottolog is collaborative work.
        </p>
        <p>
            Harald Hammarström collected many individuals' bibliographies and compiled them
            into a master bibliography.
        </p>
        <p>
            Harald also collected extensive information about the proved genealogical
            relations of the languages of the world. His top-level classification is merged
            with low-level (i.e. dialect level) information from multitree.
        </p>
        <p>
            Sebastian Nordhoff designed and programmed the database and the first version of
            the web application with help from Hagen Jung and Robert Forkel. He also took
            care of the import of the bibliographies.
        </p>
        <p>
            Robert Forkel programmed the second version of the web application as part of the
            <a href="https://clld.org">Cross Linguistic Linked Data</a> project.
        </p>
        <p>
            Martin Haspelmath gave advice at every stage throughout the project, helped with
            coordination, and is currently responsible for languoid names and dialects.
        </p>
        <p>
            Sebastian Bank made numerous improvements to the code base for the Glottolog website
            and organized the import of several large bibliographies.
        </p>
        <p>
            A table of source bibliographies for Glottolog is available at
            <a href="${request.route_url('providers')}">References information</a>.
        </p>
        <p>
            The Agglomerated Endangerment Status (AES) is derived from the databases of
            ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")}
            ,
            ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")}
            and
            ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}. For more information see
            <a href="${req.route_url('langdocstatus')}">GlottoScope</a>.
        </p>
</%util:section>


<%util:section title="Contributing" level="3" id="contributing">
    <p>
        Glottolog data is curated in a public repository at
        ${h.external_link('https://github.com/glottolog/glottolog')}.
        Please consult
        ${h.external_link('https://github.com/glottolog/glottolog/blob/master/CONTRIBUTING.md', label='the contribution guidelines')}
        for details.
    </p>
    <p>You may also look at</p>
<dl>
    <dt>${h.external_link('https://github.com/glottolog/glottolog/releases')}</dt>
    <dd>for information about released versions of Glottolog</dd>
    <dt>${h.external_link('https://github.com/glottolog/glottolog/issues')}</dt>
    <dd>for a list of issues or errata reported for Glottolog data</dd>
    <dt>${h.external_link('https://github.com/glottolog/glottolog/pulls')}</dt>
    <dd>for a list of proposed changes to Glottolog data</dd>
</dl>
</%util:section>


<%util:section title="Publications" level="3" id="publications">
    <p>
        Academic publications which deal with Glottolog include:
    </p>
    <dl>
        % for year, recs in refs.items():
        <dt>${year}</dt>
            <dd>
                <ul class="unstyled">
                    % for i, ref in enumerate(recs, start=1):
                        <li>
                            <blockquote>
                                % if isinstance(ref, h.models.Source):
                                    <strong>${h.link(req, ref)}</strong><br>
                                    <em>${ref.description}</em>
                                % else:
                                    <strong>${ref['author']}</strong> ${ref['year']}.<br>
                                    <em>${ref['title']}</em>.
                                % if 'url' in ref:
                                    <br>
                                ${h.external_link(ref['url'])}
                                % endif
                                    <br>
                                    <button type="button" class="btn btn-info btn-small" data-toggle="collapse"
                                            data-target="#bibtex-${year}-${i}">
                                        BibTeX
                                    </button>
                                    <div id="bibtex-${year}-${i}" class="collapse">
                                        <pre>${ref}</pre>
                                    </div>
                                % endif
                            </blockquote>
                        </li>
                    % endfor
                </ul>
            </dd>
        % endfor
    </dl>
</%util:section>
