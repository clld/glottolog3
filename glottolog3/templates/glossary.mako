<%inherit file="home_comp.mako"/>
<%! multirow = True %>

<div class="row-fluid">
    <div class="span10 offset1">
        <h3>Glossary</h3>
<dl>
    <dt id="Languoid">Languoid</dt>
    <dd>
        A dialect, language or language family. A more extensive definition
        can be found in
        <a href="http://ceur-ws.org/Vol-783/paper7.pdf">Nordhoff &amp; Hammarström 2011</a>
    </dd>
    <dt id="Doculect"> Doculect</dt>
    <dd>
        The language variety described in a specific document. For example,
        whatever language data is contained in a certain dictionary, grammar or
        specific article represents a unique doculect, without specifying whether that
        data constitutes an idiolect, a dialect, a variety mutually intelligible
        to some other variety or a mix of varieties from various locales.
    </dd>
    <dt id="Doctype"> Document type</dt>
    <dd>
        The class a document belongs to. There are ${doctypes.count()} classes.
        A <a href="#Lectodoc">document</a> can belong to more than one class.
        The following doctypes are distinguished
        <dl>
            % for doctype in doctypes:
            <dt id="doctype-${doctype.id}">${doctype}</dt>
            <dd>${doctype.description or ''}</dd>
            % endfor
        </dl>
    </dd>
    <dt id="macroarea">Macro-area</dt>
    <dd>
        <div class="span6 pull-right well well-small">
            <img src="${request.static_url('glottolog3:static/macroareas.png')}"/>
        </div>

        An area of the globe of roughly continent size. The following areas
        are distinguished in Glottolog/Langdoc:
        <dl>
            % for macroarea in macroareas:
            <dt id="macroarea-${macroarea.id}">${macroarea}</dt>
            <dd>${macroarea.description}</dd>
            % endfor
        </dl>
        <p>
            The division of the inhabited landmass into these macro-areas is optimal
            in the following sense. It is the division
        </p>
        <ol type="i">
            <li>into 6 areas,</li>
            <li>for which there are at least 250 languages in each area, such that</li>
            <li>the distance between the component parts inside each area is minimized, and</li>
            <li>the length of intersections between pairs of macro-areas is minimized.</li>
        </ol>
    </dd>
    <dt>Pseudo-families</dt>
    <dd>
        Sign Languages, Mixed Languages, Pidgins and Artificial Languages
        are treated as families in the database, even though they cannot be readily classified
        genealogically, These groups all share some features, which makes it convenient to
        treat them as if they were families.
    </dd>
    <dt>Unclassified languages</dt>
    <dd>
        Languages for which we have some lexical and/or grammatical information, but
        this information is so scanty that it cannot be decided whether or not
        it is genealogically related to any other language.
        They are treated as belonging to the top-level pseudo-family „Unclassified“.
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Unclassified languoid in family X</dt>
    <dd>
        A languoid for which
        <ol type="i">
            <li>
                enough lexical and/or grammatical information is
                available to assign it to a family, but for which
            </li>
            <li>
                its position within that family has not been resolved (either because of
                lack of data or because of lack of investigation).
            </li>
        </ol>
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Status in Glottolog</dt>
    <dd>
        The vast majority of languoids have the status „Established“, but there are some
        special cases: Some languages are Unattested, some are Provisional, and some
        languoids are Spurious. In addition, quite a few families have the status „Retired“.
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Unattested language</dt>
    <dd>
        <p>
            A language for which we have convincing evidence of its existence and distinctness
            from all other languages, but no grammatical or lexical
            information is available.
        </p>
        <p>
            Unattested languages can often be assigned
            to a family on non-linguistic grounds, but here they are treated as belonging
            to the pseudo-family „Unclassified“.
        </p>
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Provisional language</dt>
    <dd>
        A language whose status is currently under consideration by the Glottolog editors.
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Spurious languoid</dt>
    <dd>
        A languoid which is cited in the literature, but whose existence is
        not proven beyond doubt. This includes super-families like Amerind and
        small languages or dialects which somehow made it into other language catalogues
        without proof that they actually do exist.
        (See also the <a href="${request.route_url('glottolog.meta')}">Glottolog information</a> section.)
    </dd>
    <dt>Retired family</dt>
    <dd>
        A family which existed in Glottolog 1 (2012), but which no longer exists in the
        current version of Glottolog.
    </dd>
</dl>
    </div>
</div>
