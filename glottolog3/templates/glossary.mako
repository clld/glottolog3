<%inherit file="about_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<h3>Glossary</h3>

<%util:section title="Languoid" level="4" id="Languoid">
    <p>
        A dialect, language or language family. A more extensive definition
        can be found in
        ${h.external_link("http://ceur-ws.org/Vol-783/paper7.pdf", label=u"Nordhoff & Hammarstr\xf6m 2011")}
    </p>
</%util:section>
<%util:section title="Doculect" level="4" id="Doculect">
    <p>
        The language variety described in a specific document. For example,
        whatever language data is contained in a certain dictionary, grammar or
        specific article represents a unique doculect, without specifying whether that
        data constitutes an idiolect, a dialect, a variety mutually intelligible
        to some other variety or a mix of varieties from various locales.
    </p>
</%util:section>
<%util:section title="Document type" level="4" id="Doctype">
    <p>
        The class a document belongs to. There are ${doctypes.count()} classes.
        document can belong to more than one class.
        The following doctypes are distinguished
        <dl>
            % for doctype in doctypes:
            <dt id="doctype-${doctype.id}">${doctype}</dt>
            <dd>${doctype.description or ''}</dd>
            % endfor
        </dl>
    </p>
</%util:section>
<%util:section title="Macro-area" level="4" id="macroarea">
        <div class="span6 pull-right well well-small">
            <img src="${request.static_url('glottolog3:static/macroareas.png')}"/>
        </div>
    <p>
        An area of the globe of roughly continent size. The following areas
        are distinguished in Glottolog:
    </p>
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
    <blockquote>
        Hammarström, Harald & Mark Donohue. (2014) Principles on Macro-Areas in Linguistic Typology. <br />
        In Harald Hammarström & Lev Michael (eds.), Quantitative Approaches to Areal Linguistic Typology (Language Dynamics & Change Special Issue), 167-187. Leiden: Brill.
    </blockquote>
</%util:section>
<%util:section title="Pseudo-families" level="4">
    <p>
        Sign Languages, Mixed Languages, Pidgins and Artificial Languages
        are treated as families in the database, even though they cannot be readily classified
        genealogically, These groups all share some features, which makes it convenient to
        treat them as if they were families.
    </p>
</%util:section>
<%util:section title="Unclassified languages" level="4">
    <p>
        Languages for which we have some lexical and/or grammatical information, but
        this information is so scanty that it cannot be decided whether or not
        it is genealogically related to any other language.
        They are treated as belonging to the top-level pseudo-family „Unclassified“.
        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
    </p>
</%util:section>
<%util:section title="Unclassified languoid in family X" level="4">
    <p>
        A languoid for which
    </p>
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
    <p>
        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
    </p>
</%util:section>
## <%util:section title="Status in Glottolog" level="4">
##    <p>
##        The vast majority of languoids have the status „Established“, but there are some
##        special cases: Some languages are Unattested, some are Provisional, and some
##        languoids are Spurious. In addition, quite a few families have the status „Retired“.
##        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
##    </p>
</%util:section>
<%util:section title="Unattested language" level="4">
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
    <p>
        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
    </p>
</%util:section>
#<%util:section title="Provisional language" level="4">
#    <p>
#        A language whose status is currently under consideration by the Glottolog editors.
#        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
#    </p>
#</%util:section>
<%util:section title="Spurious languoid" level="4">
    <p>
        A languoid which is cited in the literature, but whose existence is
        not proven beyond doubt. This includes super-families like Amerind and
        small languages or dialects which somehow made it into other language catalogues
        without proof that they actually do exist.
        (See also the <a href="${request.route_url('glottolog.meta')}">Languoids information</a> section.)
    </p>
</%util:section>
#<%util:section title="Retired family" level="4">
#    <p>
#        A family which existed in Glottolog 1 (2012), but which no longer exists in the
#        current version of Glottolog.
#    </p>
#</%util:section>


<%util:section title="Most Extensive Description (MED)" level="4">
    <p>
        The Most Extensive Description (MED) for a language is the longest
        document of the highest ranking
        <a href="#Doctype">document type</a>. From highest to lowest,
        the ranking is grammar, grammar sketch, dictionary/phonology/specific
        feature/text, wordlist, followed by the remaining document types. Note that
	'description' here refers to grammatical description rather than, e.g., lexical
	documentation, so grammar trump dictionary.
    </p>
</%util:section>

<%util:section title="Descriptive status of a language" level="4">
    <p>
        The descriptive status of a language is the document type of its MED.
        For example, in the case of language for which there is a grammar
        sketch, a phonology and a dictionary, its MED would be the grammar and
        so the descriptive status would be 'grammar'. It does not matter if
        there are fifty grammars for the language or just one, the descriptive
        status would still be 'grammar'.
    </p>
</%util:section>

<%util:section title="Computerized assignment" level="4">
    <p>
        A large class of the bibliographical references have been annotated
        manually for language and document type, sometimes via a decent
        translation of another annotation scheme than the one used on
        Glottolog. However, a large class of references have not been manually
        annotated. Such references are automatically tagged on the basis of words
        that occur in the title. For example, if the title of a
        bibliographical reference contains the name of a language, it may be
        guessed to pertain to that language. Similarly, if it contains the
        word 'dictionary' it is probably of the document type dictionary.
        Which words trigger which annotations is automatically learned from
        manually tagged training data (see Hammarström 2008 for details). The
        automatic annotation is far from perfect, but is nevertheless applied
        since it does more good than harm. However, assignments which are
        triggered by words in the title in this way, as opposed to manual
        annotations, are marked as "computerized assignment".
    </p>
    <blockquote>
        Harald Hammarström. 2008. Automatic Annotation of Bibliographical References with Target Language.<br />
        Proceedings of MMIES-2: Workshop on Multi-source, Multilingual Information Extraction and Summarization, 57-64. ACL.
    </blockquote>
</%util:section>
