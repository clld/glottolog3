<%inherit file="home_comp.mako"/>

<h3>Linked Data</h3>

<div class="span4 well">
    <h4>Current version</h4>
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
    % for version, files in list(u.old_downloads(request)):
    <h4>Version ${version}</h4>
    <ul>
        % for name, url in files:
        <li><a href="${url}">${name}</a></li>
        % endfor
    </ul>
    % endfor
</div>
<div class="span7">
    <p>
        Glottolog is part of the
        ${h.external_link("http://linguistics.okfn.org/resources/llod/", label='Linguistic Linked Open Data Cloud')}.
        You can request RDF representations of the resources by adding a suitable extension
        (like '.rdf' or '.n3') in the address bar (e.g.
        <a href="${request.route_url('language', id='stan1295', ext='rdf')}">${request.route_url('language', id='stan1295', ext='rdf')}</a>),
        or by using content negotiation. Glottolog makes use of popular ontologies such as Dublin Core.
    </p>
    ##<p>
    ##    We do receive requests to access our database in JSON format. Up to now, the following requests are available.
    ##    <ul>
    ##        <li> <a href="http://glottolog.org/db/Isos?namelist=lala,mama">http://glottolog.org/db/Isos?namelist=lala,mama</a></li>
    ##        <li> <a href="http://glottolog.org/db/Nodes?name=mama">http://glottolog.org/db/Nodes?name=mama</a></li>
    ##        <li> <a href="http://glottolog.org/db/getlanguoidlist?name=mama">http://glottolog.org/db/getlanguoidlist?name=mama</a></li>
    ##        <li> <a href="http://glottolog.org/db/getlanguoidlist?iso=aaa">http://glottolog.org/db/getlanguoidlist?iso=aaa</a></li>
    ##        <li> <a href="http://glottolog.org/db/getalldescendents?id=123">http://glottolog.org/db/getalldescendents?id=123</a></li>
    ##        <li> <a href="http://glottolog.org/db/dominatedIsos?id=30024">http://glottolog.org/db/dominatedIsos?id=30024</a></li>
    ##        <li> <a href="http://glottolog.org/db/simplequery?Author=Schmidt&amp;Year=2001">http://glottolog.org/db/simplequery?Author=Schmidt&amp;Year=2001</a></li>
    ##    </ul>
    ##</p>
    ##<p>
    ##    These links might be useful for you, but they are to be treated as unsupported extra features,
    ##    which will not be documented in detail and might change without notice.
    ##</p>
    <p>
        <a href="${request.route_url('glottolog.iso', id='deu')}">${request.route_url('glottolog.iso', id='deu')}</a>
        can be used to link to a language when the ISO 639-3 code is known, but the Glottocode is unknown.
    </p>
</div>
