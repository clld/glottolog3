<%inherit file="home_comp.mako"/>
<%namespace name="g" file="helpers.mako"/>

<%g:meta_page title="Linked Data">
<div class="well">
    You can download the following items as gzipped, utf-8 encoded files:
    <dl>
        <dt>Languoids</dt>
        <dd>
            <dl>
                ##<dt>N3</dt>
                ##<dd><a href="/downloadarea/languoids.n3.tgz">languoids.n3.tgz</a></dd>
                <dt>CSV</dt>
                <dd>
                    <a href="${request.static_url('glottolog2:static/export/glottolog-languoids-utf8.csv.gz')}">
                        languoids-utf8.csv
                    </a>
                </dd>
            </dl>
        </dd>
        ##<dt>Names</dt>
        ##<dd>
        ##    <dl>
        ##        <dt>CSV</dt>
                ##<dd><a href="${h.url('/downloadarea/names.csv.zip')}">names.csv.zip</a></dd>
        ##    </dl>
        ##</dd>
        <dt>References</dt>
        <dd>
            <dl>
                <dt>BIB</dt>
                <dd>
                    <a href="${request.static_url('glottolog2:static/export/glottolog-references-utf8.bib.gz')}">
                        references-utf8.bib
                    </a>
                </dd>
                ##<dt>RDF</dt>
                ##<dd><a href="${h.url('/downloadarea/references.rdf.zip')}">references.rdf.zip</a></dd>
            </dl>
        </dd>
    </dl>
</div>
<div>
    <p>
        Glottolog is part of the
        <a href="http://linguistics.okfn.org/resources/llod/">Linguistic Linked Open Data Cloud</a>.
        You can request RDF representations of the resources by adding the extensions '.rdf' or '.n3' to
        the resource URL in the address bar (e.g.
        <a href="${request.route_url('glottolog.languoid', id='stan1295', ext='rdf')}">${request.route_url('glottolog.languoid', id='stan1295', ext='rdf')}</a>),
        or by using content negotiation. Glottolog makes use of popular ontologies such as Dublin Core,
        but some particular concepts had to be added. The Glottolog/Langdoc ontology can be found
        <a href="/ontologies/glottolog.owl">here</a>.
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
        <a href="http://glottolog.org/resource/languoid/iso/aaa">http://glottolog.org/resource/languoid/iso/aaa</a>
        can be used to link to a language when the ISO 639-3 code is known, but the Glottocode is unknown.
    </p>
    ##<p>
    ##    Furthermore, URLs of the pattern
    ##    <a href="http://www.glottolog.org/util/wikipedialink/sv/fao">http://www.glottolog.org/util/wikipedialink/sv/fao</a>
    ##    will redirect you to the wikipediapage in the first language describing the second language
    ##    (in this case the Swedish wikipedia about Faroese).
    ##</p>
</div>
</%g:meta_page>
