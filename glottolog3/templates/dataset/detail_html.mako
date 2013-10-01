<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>
<% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>

<%block name="head">
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load("feeds", "1");
    </script>
</%block>

<%def name="sidebar()">
  ${util.feed('New Grammars', 'http://glottolog.org/langdoc.atom?cq=1&doctypes=grammar', eid='grammars', linkTitle=True)}
  ${util.feed('New Languages', 'http://glottolog.org/glottolog.atom?type=languages', eid='languoids', linkTitle=True)}
  ${util.feed('New Dictionaries', 'http://glottolog.org/langdoc.atom?cq=1&doctypes=dictionary', eid='dictionaries', linkTitle=True)}
</%def>

<div class="row-fluid">
    <div class="span12">
        <h2>Welcome to Glottolog</h2>
    <p class="lead">
        Comprehensive reference information for the world's languages, especially the
        lesser known languages.
    </p>
    <p>
        Information about the different languages,
        dialects, and families of the world ('languoids') is available in the
        <a href="${request.route_url('languages')}" title="glottolog">Languoid</a>
        section. The
        <a href="${request.route_url('sources')}" title="langdoc"> Langdoc</a>
        section contains bibliographical information.
        You can query the bibliographical database with  in the
        <a href="${request.route_url('sources')}" title="bibliographical query">a normal query</a>
        or a
        ##<a href="${request.route_url('langdoc.complexquery')}" title="complex query">complex query</a>
        ##involving genealogical affiliation, document type, and macro-area.
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
        <h3>Languoid catalogue</h3>
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
        <h3>Langdoc</h3>
        <p>
            <strong><a href="${request.route_url('sources')}" title="langdoc"> Langdoc </a></strong>
            is a comprehensive collection of bibliographical data for the world's lesser
            known languages. It provides access to more than 180,000 references of descriptive works such as
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
            Glottolog is an initiative of the Max Planck Institute for Evolutionary
            Anthropology. It should be cited as follows:
        </p>
<blockquote>
    ${h.newline2br(TxtCitation.render(ctx, request))|n}
</blockquote>
        <p>
            Particularly important contributors to the Langdoc database are Alain Fabre,
            Jouni Maho and SIL International. For more details, see the
            <a href="${request.route_url('home.credits')}" title="credits">Credits</a> page.
        </p>
    </div>
</div>

