<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>
<% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>

<%def name="sidebar()">
  ${util.feed('New Grammars', request.route_url('sources_alt', ext='atom', _query=dict(cq=1, doctypes='grammar', year=str(h.datetime.date.today().year))), eid='grammars', linkTitle=True, numEntries=3)}
  ${util.feed('New Languages', request.route_url('languages_alt', ext='atom', _query=dict(type='languages')), eid='languoids', linkTitle=True, numEntries=3)}
  ${util.feed('New Dictionaries', request.route_url('sources_alt', ext='atom', _query=dict(cq=1, doctypes='dictionary', year=str(h.datetime.date.today().year))), eid='dictionaries', linkTitle=True, numEntries=3)}
</%def>

<div class="row-fluid">
    <div class="span12">
        <h2>Welcome to ${ctx.name}</h2>
    <p class="lead">
        Comprehensive reference information for the world's languages, especially the
        lesser known languages.
    </p>
    <p>
        Information about the different languages,
        dialects, and families of the world ('languoids') is available in the
        <a href="${request.route_url('languages')}" title="glottolog">Languages</a> and
        <a href="${request.route_url('glottolog.families')}">Families</a>
        sections. The
        <a href="${request.route_url('sources')}" title="langdoc"> References</a>
        section contains bibliographical information.
        You can query the bibliographical database by filtering the table view or using
        <a href="${request.route_url('langdoc.complexquery')}" title="complex query">a complex query</a>
        involving genealogical affiliation, document type, and macro-area.
    </p>
    </div>
</div>

<div class="row-fluid">
    <div class="span4">
        <div class="well well-small">
            <img src="${request.static_url('glottolog3:static/World_Map.jpg')}"/>
        </div>
    </div>
    <div class="span8">
        <h3>Catalogue of languages and families</h3>
        <p>
            <strong>Glottolog</strong> provides a
            <a href="${request.route_url('languages')}" title="languoids">comprehensive catalogue</a>
            of the world's languages, language families and dialects.
            It assigns a unique and stable identifier (the Glottocode) to (in principle) all languoids,
            i.e. all families, languages, and dialects. Any variety that a linguist works on should
            eventually get its own entry. The languoids are organized via a genealogical classification
            (the Glottolog tree) that is based on available historical-comparative research
            (see also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section).
        </p>
    </div>
</div>

<div class="row-fluid">
    <div class="span8">
        <h3>Bibliography</h3>
        <p>
            The <a href="${request.route_url('sources')}" title="langdoc">References </a>
            section ('langdoc') provides a comprehensive collection of bibliographical data for the world's lesser
            known languages. It provides access to ${numrefs} references of descriptive works such as
            grammars, dictionaries, word lists, texts etc. Search criteria include author, year, title,
            country, and genealogical affiliation. References can be downloaded as txt, bib, html,
            or with the
            <a href="http://www.zotero.org"><i class="icon-share"> </i>Zotero</a>
            Firefox plugin.
        </p>
    </div>
    <div class="span4">
        <div class="well well-small">
            <img src="${request.static_url('glottolog3:static/nebrija.jpg')}"/>
        </div>
    </div>
</div>

<div class="row-fluid">
    <div class="span12">
        <p>
            Glottolog will be continuously expanded and improved with the help
            of their users. The input of expert linguists is crucial.
        </p>
        <p>
            Glottolog is an initiative of the Max Planck Institute for
            Evolutionary Anthropology, Leipzig. It should be cited as follows:
        </p>
<blockquote>
    ${h.newline2br(TxtCitation.render(ctx, request))|n}<br>
    <a href="https://doi.org/${u.DOI}"><img src="https://zenodo.org/badge/DOI/${u.DOI}.svg" alt="DOI"></a>
</blockquote>
        <p>
            Particularly important contributors to the Langdoc database are Alain Fabre,
            Jouni Maho and SIL International. For more details, see the
            <a href="${request.route_url('home.credits')}" title="credits">Credits</a> page.
        </p>
        <p>
            The data published by Glottolog is curated in the public GitHub repository
            ${h.external_link("https://github.com/glottolog/glottolog", label='glottolog/glottolog')}.
            The Glottolog web application at https://glottolog.org serves the latest
            ${h.external_link("https://github.com/glottolog/glottolog/releases", label='released version')}
            of the data in this repository.
        <p>
            You may report errors you found in Glottolog using this repositories
            ${h.external_link("https://github.com/glottolog/glottolog/issues", label='issue tracker')}.
        </p>
    </div>
</div>
