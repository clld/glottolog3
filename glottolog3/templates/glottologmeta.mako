<%inherit file="glottolog_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! multirow = True %>

<div class="row-fluid">
    <div class="span10 offset1">
        <%util:section title="Languoids Information" prefix="">
        </%util:section>
    </div>
</div>

<div class="row-fluid">
    <div class="span3 offset1">
        <div class="well well-small">
            <img src="${request.static_url('glottolog3:static/stammbaum.png')}"/>
        </div>
    </div>
    <div class="span7">
        <p>
            Glottolog aims to provide a comprehensive list of languoids (families, languages,
            dialects, chronolects, eventually sociolects) that linguists need to talk about. Each
            languoid has a unique and persistent identifier called <strong>Glottocode</strong>,
            consisting of four letters and four digits [abcd1234].
        </p>
        <p>
            Currently ${str(last_update).split(' ')[0]} the number of (extinct or living) languages are as follows:
        </p>
        <table class="table table-striped">
            <tbody>
                <tr>
                    <th>Spoken L1 Languages</th>
                    <td class="right">
                        ${number_of_languages['l1']}
                        <!--p>***# leaves in lff.txt + #Unclassified lof.txt + Mixed Languages in lof.txt + unattested Languages in lof.txt *** </p-->
                    </td>
                </tr>
                <tr>
                    <th>Artificial Spoken Languages</th>
                    <td class="right">
                        ${number_of_languages['artificial']}
                        <!--p>*** # artifical in lof.txt *** </p-->
                    </td>
                </tr>
                <tr>
                    <th>Sign Languages and Auxiliary Sign Systems</th>
                    <td class="right">
                        ${number_of_languages['sign']}
                        <!--p>*** # sign in lof.txt *** </p-->
                    </td>
                </tr>
                <tr>
                    <th>Pidgin Languages</th>
                    <td class="right">
                        ${number_of_languages['pidgin']}
                        <!--p>*** # pidgin in lof.txt *** </p-->
                    </td>
                </tr>
                <tr>
                    <td> </td>
                    <td class="right">
                        ${number_of_languages['all']}
                        <!--p>*** sum of the above *** </p-->
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<div class="row-fluid">
    <div class="span10 offset1">
        <div style="float: right;" class="span5 well well-small">
            <img src="${request.static_url('glottolog3:static/World_Map.jpg')}"/>
        </div>
    <p>
        Languages are classified (see below) into ${number_of_families} and
        ${number_of_isolates} isolates, i.e., one-member families, and a few other
        categories (sign, pidgin, mixed language etc). This classification is the best guess
        by the Glottolog editors and the classification principles are described in the schema
        below. Users should be aware that for many groups of languages, there is little available
        historical-comparative research, and are subject to change as scholarship and interest in
        those language increase. Please contact the editors if you have corrections to the language
        classification.
    </p>
    <p>
        Language classification tends to mix the notions of <em>member</em> and <em>child</em>.
        The subtle differences between Latin, Proto-Romance and the Romance language family
        are normally disregarded. This does not create problems 99% of the time, but becomes
        problematic when automatic reasoners are applied.
        <a href="${request.route_url('language', id='stan1290')}">French</a> is not a <em>member</em> of
        <a href="${request.route_url('language', id='lati1261')}">Latin</a>
        for instance, but it is a <em>member</em> of
        <a href="${request.route_url('language', id='roma1334')}">Romance</a>.
        At this stage of the project, we
        separate paleolects (earlier varieties) from the purely set theoretic tree. A paleolect
        can never have children. In future versions of Glottolog, a more detailed modeling may
        be provided.
    </p>

    <%util:section title="Principles" prefix="">
    <p>
        Every putative language is considered according to the decision procedure in
        <a href="#x1-10011">Figure 1</a>.
        All spoken languages for which a sufficient amount of linguistic data exists&mdash;the decision
        tree leaves with double boxes around them&mdash;are deemed classifiable, and are classified
        into genealogical families (and isolates). The other kinds of languages are filed into
        other categories. The listing is complete only for classifiable languages. Regarding
        unattested, unclassifiable and spurious languages, see <a href="${request.route_url('source', id=308733)}">Harald Hammarström (2012)</a>. A comprehensive
        listing of pidgins is <a href="${request.route_url('source', id=129370)}">Peter Bakker and Mikael Parkvall (2010)</a>. This listing differentiates different levels of
        evidence for the existence of a pidgin, rather than a strict yes/no existence-decision.
        There are extensive lists of sign languages (<a href="${request.route_url('source', id=45973)}">Taylor, Allan R. 1996</a>, <a href="${request.route_url('source', id=314571)}">J. Albert Bickford 2005</a>, <a href="${request.route_url('source', id=114593)}">Kamei, Nobutaka 2004</a>, <a href="${request.route_url('source', id=314546)}">Ulrike Zeshan 2006</a>, <a href="${request.route_url('source', id=314580)}">Roger Blench and Andy Warren 2003</a>, <a href="${request.route_url('source', id=161311)}">Anonymous 2007</a>),
        whistled languages (<a href="${request.route_url('source', id=108497)}">Julien Meyer 2005</a>) and artificial languages (<a href="${request.route_url('source', id=314581)}">P. O. Bartlett 2006</a>).
     <!--l. 86--></p>
    </%util:section>

    <div class="well well-small">
        <a id="x1-10011"></a>
        <a href="${request.static_url('glottolog3:static/lfintro.png')}">
        <img src="${request.static_url('glottolog3:static/lfintro.png')}" alt=""/>
        </a>
        <caption>
         <span class="id">Figure&#160;1: </span>
         <span class="content">Decision procedure for inclusion in the present language listing.</span>
        </caption>
    </div>

            <%util:section title="Inclusion/Exclusion of Languages" prefix="" level="4">
    <h5><a id="x1-3000"></a>1. Is the putative language assertably distinct from all other known languages?</h5>
    <p>
        For any alleged language to be considered in the classification we must first determine whether it was
        distinct from all other languages. By distinct, we mean <em>not mutually intelligible</em>
        with any other language. In principle, any convincing evidence to this effect is sufficient. For example,
        direct comparison of language data or testimonies of non-intelligibility to all neighbouring languages
        is the most straightforward kind of evidence. But also, e.g., evidence (archaeological, aerial, ethnographic)
        isolation from all other humans for a long time could make a convincing case that a language is indeed
        distinct from all others.
    </p>
    <p>
        For example, Flecheiros is the name given to an uncontacted group in the Javari valley in Western Brazil
        (<a href="${request.route_url('source', id=85197)}">Carlos Alberto Ricardo 1986</a>). Ethnographic evidence suggests that they, if akin to anyone in the vicinity, are Kanamari
        (a known Katukinan language, see, e.g., <a href="${request.route_url('source', id=9415)}">Zoraide dos Anjos 2011</a>). However, <a href="${request.route_url('source', id=311488)}">Scott Wallace (2011)</a> recounts one meeting between a
        Kanamari and the Flecheiros revealing that they do not speak intelligible languages (though one Kanamari
        women captured at an early age was living among the Flecheiros). Even if not totally foolproof, this
        appears to be convincing evidence that the Flecheiros speak a language distinct from all others.
    </p>
    <p>
        However, all the pieces of evidence must be present. There are plenty of other cases where a speech form
        (often extinct) is known not to have been unintelligible to some or most languages around it
        (e.g., Yalakalore in <a href="${request.route_url('source', id=37160)}">David M. Eberhard 2009</a>), but this is not sufficient if it cannot be asserted for
        <em>every</em> plausible candidate. A further caveat is that testimonies must themselves be convincing
        to count as testimonies. There are cases where unintelligibility information comes from individuals who
        were in no position to judge it, e.g., they might be passing on hearsay, or pass on some kind of general
        impression not based solely on language.
    </p>
    <h5><a id="x1-4000"></a>2. Are there form-meaning pairs?</h5>
    <p>
        For a linguistic classification, we naturally require that actual linguistic data, i.e., form-meaning pairs
        (as opposed to purely sociolinguistic data), form the basis for the classification. That means that some
        linguistic data has been collected which provides the basis for classification, but does not necessarily
        mean that the data in question has been published. We also require that the data is not known to have
        vanished, meaning that once attested languages whose attestation now appears to be lost count as unattested.
        For example, grammar sketches of three extinct South American language Taimviae, Teutae and Agoiae that once
        did exist (<a href="${request.route_url('source', id=45004)}">Daniel G. Brinton 1898</a>):203,208 now seem to have vanished completely. Thus, the three count as unattested
        because it is known that the attestation is gone.
    </p>
    <h5><a id="x1-5000"></a>3. Has it served as the main means of communication for a human society?</h5>
    <p>
        There are two reasons for restricting the scope to communication systems that serve(d) as the main means of
        communication for a human society.
    </p>
    <p>
        First, language classification (see below) by the comparative method explicitly or implicitly assumes that
        language change is governed by certain (vaguely formulated) probabilistic laws. These laws have a plausible
        theoretical foundation if the communication system serve(d) as the main means of communication for a human
        society, but do not necessarily apply to all forms of normed human communication systems. For example,
        radical vocabulary replacement within one generation of speakers would be highly unlikely for a main means
        of communication of a society (communication would break down!), but might be possible in an auxiliary
        communication system taught to adults. Similarly, sound change is though to come about as humans hear and
        (mis)interpret spoken analog communication (<a href="${request.route_url('source', id=314555)}">John J. Ohala 1993</a>, <a href="${request.route_url('source', id=314558)}">Brown, Cecil H. and Eric W. Holman and Søren Wichmann 2013</a>) and would, for that reason, not be
        expected in, e.g., computer programming languages.
    </p>
    <p>
        Second, one of the purposes for doing language classification in the first place is to obtain insights
        into the history of its speakers. All human societies have a main means of communication, so such a
        communication system reflects the history of a human society. It is not necessarily the case that all
        forms of normed human communication systems reflect the history of its speakers. For example, a whistled
        language may come and go in the course of history of a people, whereas a people cannot be without a main
        speech form for any period of history.
    </p>
    <h5><a id="x1-6000"></a>4. Is the modality speech?</h5>
    <p>
        The present classification of languages is restricted to spoken languages for the sole reason that there
        exists a methodology for establishing genealogical relationships is known for spoken languages (<a href="${request.route_url('source', id=94097)}">Campbell, Lyle and Poser, William J. 2008</a>).
        This is not necessarily the case for signed languages.
    </p>
    <h5><a id="x1-7000"></a>5. Are the form-meaning pairs enough to distinguish between different classification proposals?</h5>
    <p>
        We also require that the amount of form-meaning pairs is sufficient for a classification. There is no
        universal fix threshold for how much is sufficient as this depends on how closely related the language is
        to other known languages. An approximate minimal requirement is 50 items or so of basic vocabulary, i.e.,
        not personal names or special domain vocabulary. For example, the extinct Gamela of Northeastern Brazil is
        known from 19 words only (<a href="${request.route_url('source', id=47776)}">Curt Nimuendajú 1937</a>:68)&mdash;hardly enough for a classification. It is arguable that the
        sound-values encoded in the Linear A script can be gauged, but little, if any, meaning can be inferred
        (<a href="${request.route_url('source', id=18847)}">Yves Duhoux 1998</a>, <a href="${request.route_url('source', id=145800)}">Best, Jan 1989</a>, <a href="${request.route_url('source', id=10744)}">K. Aartun 1997</a>), rendering the data insufficient for classification.
    </p>
            </%util:section>
            <%util:section title="Classification" prefix="" level="4">
    <h5>
        <a id="x1-9000"></a>
        6. Are the form-meaning similarities to at least one other language best explained by inheritance from a common ancestor?
    </h5>
    <p>
        Given a language with sufficient attestation, one can compare it with the remaining languages. If there are
        similarities to other language(s) that can be shown exceed chance, there are three possible kinds of
        explanations: universals, contact or inheritance from a common ancestor (<a href="${request.route_url('source', id=94097)}">Campbell, Lyle and Poser, William J. 2008</a>). If the best explanation
        for the similarities are inheritance from common ancestor, languages are classified as belonging to the same
        family. A language which, by this principle, does not belong to the same family as any other language is also
        called an isolate. What constitutes the &ldquo;best&rdquo; explanation is not a static judgment, but subject to change as
        new considerations and new data appear. For example, some lexical parallels between Nadahup, Kakua-Nukak and
        Puinave (<a href="${request.route_url('source', id=158063)}">Rivet, Paul and Constant Tastevin 1920</a>) were for a long time considered by many to be &ldquo;best&rdquo; explained by a genealogical
        relationship. However, thanks to increased documentation and interest in the languages, the explanation of
        the similarities as loans, chance resemblances and even data errors, is now favoured
        (<a href="${request.route_url('source', id=60268)}">Patience Epps 2008</a>:5-9, <a href="${request.route_url('source', id=153689)}">Katherine Bolaños and Patience Epps 2009</a>, <a href="${request.route_url('source', id=21440)}">Katherine Bolaños 2011</a>, <a href="${request.route_url('source', id=138662)}">Girón, Jesús Mario 2008</a>:419-439). Not only the state of documentation and investigation
        of specific groups may alter the perceived &ldquo;best&rdquo; explanation, but also new arguments regarding the probative
        value of various kinds of evidence. For example, <a href="${request.route_url('source', id=21928)}">Malcolm Ross (1995)</a>, <a href="${request.route_url('source', id=148196)}">Malcolm Ross (2001)</a>, <a href="${request.route_url('source', id=10496)}">Ross, Malcolm (2005)</a> argues that similarities
        in pronoun signatures can be used to create preliminary groupings of Papuan languages, whereas <a href="${request.route_url('source', id=314563)}">Harald Hammarström (2012)</a>,
        using data from all over the world, argues that such usage of the evidence is not probative for genealogical
        groupings.
    </p>
    <p>
        There is the theoretical possibility that a language with sufficient attestation has simply not (yet) been
        compared to other relevant languages to determine if there are any non-random similarities. In practice, we
        know of no such language, and therefore have no separate category for languages inhabiting this logical
        possibility.
    </p>
    <p> </p>
    <h5><a id="x1-10000"></a>7. Has there been sufficient comparison to determine its closest relative(s)?</h5>
    <p>
        Given a language and the other languages that belong to the same family, if insufficient data is available or
        insufficient comparative work has been done to determine the closest relative(s) of the language at hand, it
        is left unclassified within the finest-level (sub)family that can be discerned.
    </p>
    <p>
        For example, the subgrouping study of the Greater Awyu subfamily by <a href="${request.route_url('source', id=304684)}">Lourens de Vries and Ruth Wester and Wilco van den Heuvel (2012)</a> uses shared innovations in
        verb morphology as the most reliable indicator of linguistic ancestry because, in a landscape of dialect
        chains and clan loyalty shifts (<a href="${request.route_url('source', id=305807)}">de Vries, Lourens J. 2012</a>), lexicon and phonology is thought to be particularly vulnerable
        to diffusion. Within the Greater Awyu languages, there is a binary split between the Becking-Dawi group and
        the Awyu-Dumut groups. Awyu-Dumut, in turn, divides into three large dialect chains Awyu, Dumut and Ndeiram.
        For one language (clearly belonging to the Greater Awyu family on lexical and pronominal grounds), Sawi, no
        morphological data is available, so, for lack of data on verb morphology, its position within the subfamily
        cannot be determined and it is consequently left unclassified within it.
    </p>
    <p>
        In other cases, data availability is not the bottleneck, but the work required to ascertain the subgrouping.
        Plenty of data exists for Adamawa Fali and other Volta-Congo languages (although patchily distributed), but
        subgrouping in the Volta-Congo languages is a large and complicated issue, leaving the subgrouping of
        Adamawa Fali unresolved (<a href="${request.route_url('source', id=114627)}">Boyd, Raymond 1989</a>):180.
    </p>
    <h5><a id="x1-11000"></a>8. Is there a subgrouping based on shared innovations?</h5>
    <p>
        The preferred subgrouping criterion is a subgrouping based on shared innovations (<a href="${request.route_url('source', id=98107)}">Malcolm Ross 1988</a>, <a href="${request.route_url('source', id=302679)}">Malcolm Ross 1997</a>).
        For each language where such is available, that subgrouping is followed.
    </p>
    <h5><a id="x1-12000"></a>9. Are there other, weaker, arguments for subgrouping?</h5>
    <p>
        If no subgrouping based on shared innovations is available, whatever other (weaker) arguments are considered.
        Weaker arguments would be shared similarities in general, e.g., lexicostatistics, which may reflect borrowings
        and/or retentions. The subgrouping of the least bad such evidence is followed. For example, two independent
        published opinions exist on the internal subgrouping of the Mek languages, namely that of <a href="${request.route_url('source', id=37015)}">Volker Heeschen (1978)</a>,
        <a href="${request.route_url('source', id=34449)}">Volker Heeschen (1992)</a> and that which appears in <a href="${request.route_url('source', id=38805)}">Peter J. Silzer and Heljä Heikkinen-Clouse (1991)</a>. The former gives a lexicostatistical argument for a
        subgrouping while the latter lists a subgrouping without pointing to any evidence at all. The lexicostatistical
        evidence is preferrable to no evidence at all, and is therefore followed.
    </p>
            </%util:section>
            <%util:section title="Accountability" prefix="" level="4">
    <p>
        The outcome classification is presented in the glottolog tree. Detailed evidence that the presented classification
        actually conforms to the principles above is provided in the form of references to work containing or subsuming
        the required evidence for the decisions reflected in the classification.
    </p>
    <p>
        On the leaf level, i.e., for languages, references to actual data for each language are given, justifying principles 1-5.
    </p>
    <p>
        For the classification, principles 6-9, references justifying nodes are displayed in the green box below the
        tree-fragment box. Wherever necessary, a comment accompanies the reference if the decision reflected in the
        tree does not follow straightforwardly from the argumentation in the references work(s).
    </p>
    <p>
        We do not always conform to the interpretation and conventions of the authors cited as justification. It may be,
        for example, that an author states that a certain group should be assumed on purely geographic grounds, in
        anticipation of future work, or some other reason not admissible as justification in the present classification.
        In such cases, the justificational value of the reference is on the (lack of) evidence and/or arguments found
        in the reference, not necessarily the interpretation of this state given in that reference.
    </p>
            </%util:section>
            <%util:section title="Names of Families and Subfamilies" prefix="">
    <p>
        Whenever possible, current from the literature names of families and subfamilies are taken over. This is
        considered possible when there is no name clash (with another language or (sub-)family in the world) and
        the name in the literature in principle refers to the intended set of languages. If the (sub-)family in the
        present classification differs in any significant way from that associated with a certain name, we have
        introduced a new unique name which is in often not found in the literature. The new names are all unique
        and unambiguous but there is otherwise little effort spent on finding the name optimal in describing its set
        of languages (e.g., with the name of a central river or by taking the word for &ldquo;man&rdquo;) or optimal in the system
        of names in the region or greater family (e.g., by using a name with a Spanish flavour if the surrounding
        (sub-)families have Spanish-flavoured names). A number of names may look somewhat artificial
        (e.g., Nuclear A, or, A-B-C) or out of place (e.g., a subfamily with an Anglophone name whose parent has a
        Francophone name), reflecting the fact that no particular value is attached to names beyond being unique and
        unambiguous.
    </p>
            </%util:section>
            <%util:section title="Example" prefix="">
    <p>
        For example, <a href="${request.route_url('language', id='tuca1253')}">Tucanoan</a> is a
        South American language family. <a href="${request.route_url('source', id=310719)}">Chacon, Thiago C. (2012)</a> contains a subgrouping based on
        shared phonological innovations and defines the position in the tree for all the below nodes except
        Arapaso, Miriti, Macaguaje and Tama, which fall outside the scope of his study. Thus, <a href="${request.route_url('source', id=310719)}">Chacon, Thiago C. (2012)</a> is given
        as the reference justifying the top-level family as well as the reference justifying most intermediate nodes.
        The remaining languages, Arapaso, Miriti, Macaguaje and Tama do exist (or did exist) and they are arguably
        Tucanoan. For Macaguaje and Tama, a small amount of data is attested and published, and this is enough for
        <a href="${request.route_url('source', id=56760)}">Sergio Elías Ortiz (1965)</a>:133 to show that they are within the
        <a href="${request.route_url('language', id='sion1248')}">Siona-Secoya</a>
        group. Thus, here <a href="${request.route_url('source', id=56760)}">Sergio Elías Ortiz (1965)</a>:133 is cited as
        the reference justifying the position of Macaguaje and Tama. For Miriti and Arapaso, <a href="${request.route_url('source', id=9035)}">Brüzzi Alves da Silva, Alcionilio (1972)</a> collected
        short wordlists of them, and concluded that they were Tucanoan, but he gives no further information that would
        allow us to infer their relation to each other or to other Tucanoan languages. The wordlists themselves were
        never published, and are possibly now lost (but this is not certain). Hence, Arapaso and Miriti are labeled
        <a href="${request.route_url('language', id='uncl1448')}">Unclassified Tucanoan</a> languages.
        There is no implication that Arapaso and Miriti would form a subgroup in the
        sense of having a common ancestor unique only to them.
    </p>
            </%util:section>
    <%util:section title="Acknowledgements" prefix="">
    <p>Thanks </p>
    <ul class="itemize1">
        <li class="itemize">To Tim Usher for many points of dicussion re Papuan languages </li>
        <li class="itemize">To Mark Donohue for many points of dicussion re Papuan and Austronesian languages </li>
        <li class="itemize">To Matthew Dryer for many points of dicussion re Papuan and other languages </li>
        <li class="itemize">To Roger Blench for all things Nigerian and beyond </li>
        <li class="itemize">To Bonny Sands for help with access to various valuable documents </li>
        <li class="itemize">To Mikael Parkvall for help with &ldquo;Creole&rdquo; language classification </li>
        <li class="itemize">To Willem Adelaar for many points of discussion re South American languages </li>
        <li class="itemize">To all authors of descriptive and comparative works on the languages of the world </li>
        <li class="itemize">To 25 libraries for access and services </li>
        <li class="itemize">To over 250 individuals who provided confirming and/or clarificatory information</li>
    </ul>
    </%util:section>
</div>
