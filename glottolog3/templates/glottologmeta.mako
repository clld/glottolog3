<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%! multirow = True %>

<div class="row-fluid">
    <div class="span10 offset1">
            <%util:section title="About Languoids" prefix="">
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
            dialects) that linguists need to be able to identify. Each
            languoid has a unique and persistent identifier called <strong>Glottocode</strong>
            (<a href="https://content.iospress.com/articles/semantic-web/sw212843">Hammarström and Forkel (2022)</a>),
            consisting of four alphanumeric characters (i.e. lowercase letters or decimal digits) and four decimal
            digits (<span style="font-family: monospace">abcd1234</span> follows this patters, but so does
            <a href="/resource/languoid/id/b10b1234"><span style="font-family: monospace">b10b1234</span></a>).
        </p>
        <p>
            Currently ${str(last_update).split(' ')[0]} there are
            <strong>${number_of_languages['Spoken L1 Language']} spoken L1 languages</strong>
            (i.e. spoken languages traditionally used by a community of speakers as their first language).
        </p>
        <p>
            Languages are classified (see below) into <strong>${number_of_families} families</strong> and
            <strong>${number_of_isolates} isolates</strong>, i.e., one-member families.
            This classification is the best guess
            by the Glottolog editors and the classification principles are described in <a href="#x1-10011">Figure 1</a>
            below and the accompanying text. Users should be aware that for many groups of languages, there is little
            available
            historical-comparative research, so the classifications are subject to change as scholarship and interest in
            those languages increase. Please contact the editors if you have corrections to the language
            classification.
        </p>
        <p>
            In addition to the genealogical trees (families and isolates), the Families page also includes the following
            <strong>non-genealogical trees</strong>:
        </p>
        <ul>
            % for key in [k for k in number_of_languages if k not in ['Bookkeeping', 'Spoken L1 Language']]:
                <li>${key}</li>
            % endfor
        </ul>
        <p>
            (Glottolog also contains lists of putative languages that are not regarded as real languoids by
            the editors but that are given a Glottocode for bookkeeping purposes;
            these are called <strong>bookkeeping languoids</strong> and they are described further below.)
        </p>
    </div>
</div>

<div class="row-fluid">
    <div class="span5 offset1">
        <table class="table table-striped" style="float: inline;">
            <tbody>
                % for label, count in number_of_languages.items():
                    <tr>
                        <th>${label}</th>
                        <td class="right">${'{0:,}'.format(count)}</td>
                    </tr>
                % endfor
            <tr>
                <td>All</td>
                <td class="right">${'{0:,}'.format(sum(number_of_languages.values()))}</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="span5">
        <div style="float: right;" class="span9 well well-small">
            <img src="${request.static_url('glottolog3:static/World_Map.jpg')}"/>
        </div>
    </div>
</div>


<div class="row-fluid">
    <div class="span10 offset1">

        <%util:section title="Principles" prefix="">
            <p>
                Every putative language is considered according to the decision procedure in
                <a href="#x1-10011">Figure 1</a>.
                All spoken languages for which a sufficient amount of linguistic data exists&mdash;the leaves of the
                decision
                tree with double boxes around them&mdash;are deemed classifiable, and are classified
                into genealogical families (and isolates). The other kinds of languages are filed into
                the other categories that were listed above. Glottolog is complete only for classifiable languages.
                Regarding
                unattested and unclassifiable languages, see <a href="${request.route_url('source', id=476024)}">Harald
                Hammarström (2015)</a>.
                A comprehensive listing of pidgins is <a href="${request.route_url('source', id=129370)}">Peter Bakker
                and Mikael Parkvall (2010)</a>.
                This listing differentiates different levels of
                evidence for the existence of a pidgin, rather than a strict yes/no existence-decision.
                ${u.format_comment(request, """Elsewhere there are extensive lists of whistled languages (**hh:h:Meyer:Whistled:2015**,
        **hh:h:BusnelClasse:Whistled**, **hh:e:Harrisson:Borneo-Nomads**, **hh:h:Thierry:Siffles**), initiation languages (**hh:ld:Ngonga-ke-Mbembe:Initiatique-Ohendo**, **hh:h:James:Speech-Surrogates**, **hh:typ:Monino:Labi**, ritual languages **hh:ld:Brindle:Kiliji**), secret languages (**hh:ld:Dugast:Njoya**,**hh:s:Ittman:Nixenkultbundes**,**hh:w:Beaujard:Arabico-Malgache**, **hh:ldsoc:Berjaoui:Amazigh-Secret**, **hh:soc:Berjaoui:Moroccan**, **hh:s:Leiris:Dogons**, **hh:hvld:Leslau:Ethiopian-Argots**, **hh:h:Debrunner:Vergessene-Togorestvolkern**, **hh:hw:Thomas:Southern-Nigeria**, **hh:h:James:Speech-Surrogates**) and drummed languages (**hh:ld:Betz:Trommelsprache-Duala**, **hh:ld:Carrington:Gong**, **hh:ld:Arom:Tambourine-Banda-Linda**, **hh:ld:Seifart:Bora-Drum**, **hh:typ:Stern:Drum**, **hh:ld:Aitken:Drum**, **hh:h:James:Speech-Surrogates**).""")|n}
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

        <%util:section title="Inclusion/exclusion of languages" prefix="" level="4">
            <h5><a id="x1-3000"></a>1. Is the putative language assertably distinct from all other known languages?</h5>
            <p>
                For any alleged language to be considered in the classification we must first determine whether it was
                distinct from all other languages. By distinct, we mean <em>not mutually intelligible</em>
                with any other language. In principle, any convincing evidence to this effect is sufficient. For
                example,
                direct comparison of language data or testimonies of non-intelligibility to all neighbouring languages
                is the most straightforward kind of evidence. But also, various types of evidence
                for isolation from all other humans for a long time could make a convincing case that a language is
                indeed
                distinct from all others.
            </p>
            <p>
                For example, Flecheiros is the name given to an uncontacted group in the Javari valley in Western Brazil
                (<a href="${request.route_url('source', id=85197)}">Carlos Alberto Ricardo 1986</a>). Ethnographic
                evidence suggests that they, if akin to anyone in the vicinity, are Kanamari
                (a known Katukinan language, see, e.g., <a href="${request.route_url('source', id=9415)}">Zoraide dos
                Anjos 2011</a>). However, <a href="${request.route_url('source', id=311488)}">Scott Wallace (2011)</a>
                recounts one meeting between a
                Kanamari and the Flecheiros revealing that they do not speak intelligible languages (though one Kanamari
                woman captured at an early age was living among the Flecheiros). Even if not totally foolproof, this
                appears to be convincing evidence that the Flecheiros speak a language distinct from all others.
            </p>
            <p>
                However, all the pieces of evidence must be present. There are plenty of other cases where a speech form
                (often extinct) is known not to have been unintelligible to some or most languages around it
                (e.g., Yalakalore in <a href="${request.route_url('source', id=37160)}">David M. Eberhard 2009</a>), but
                this is not sufficient if it cannot be asserted for
                <em>every</em> plausible candidate. A further caveat is that testimonies must themselves be convincing
                to count as testimonies. There are cases where unintelligibility information comes from individuals who
                were in no position to judge it, e.g., they might be passing on hearsay, or pass on some kind of general
                impression not based solely on language.
            </p>
            <p>
                If a putative language is or was not considered as a distinct language by these criteria,
                it is either a dialect of a language, or it is classified as “based on misunderstanding”.
                In the latter case, it is listed as a type of bookkeping languoid (see below).
            </p>
            <h5><a id="x1-4000"></a>2. Are there form-meaning pairs?</h5>
            <p>
                For a linguistic classification, we naturally require that actual linguistic data, i.e., form-meaning
                pairs
                (as opposed to purely sociolinguistic data), form the basis for the classification. That means that some
                linguistic data has been collected which provides the basis for classification, but does not necessarily
                mean that the data in question has been published. We also require that the data is not known to have
                vanished, meaning that once attested languages whose attestation now appears to be lost count as
                unattested.
                For example, grammar sketches of three extinct South American language Taimviae, Teutae and Agoiae that
                once
                did exist (<a href="${request.route_url('source', id=45004)}">Daniel G. Brinton 1898</a>:203, 208) now
                seem to have vanished completely. Thus, the three count as unattested
                because it is known that the attestation is gone.
            </p>
            <h5><a id="x1-5000"></a>3. Has it served as the main means of communication for a human society?</h5>
            <p>
                There are two reasons for restricting the scope to communication systems that serve(d) as the main means
                of
                communication for a human society.
            </p>
            <p>
                First, language classification (see below) by the comparative method explicitly or implicitly assumes
                that
                language change is governed by certain (vaguely formulated) probabilistic laws. These laws have a
                plausible
                theoretical foundation if the communication system serve(d) as the main means of communication for a
                human
                society, but do not necessarily apply to all forms of normed human communication systems. For example,
                radical vocabulary replacement within one generation of speakers would be highly unlikely for a main
                means
                of communication of a society (communication would break down!), but might be possible in an auxiliary
                communication system taught to adults. Similarly, sound change is though to come about as humans hear
                and
                (mis)interpret spoken analog communication (<a href="${request.route_url('source', id=314555)}">John J.
                Ohala 1993</a>, <a href="${request.route_url('source', id=314558)}">Brown, Cecil H. and Eric W. Holman
                and Søren Wichmann 2013</a>) and would, for that reason, not be
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
            <p>
                If a putative language is not the main means of communication for a society,
                it is classified as a pidgin or as a speech register.
                (Neither whistled or drummed languages nor jargons are currently included in Glottolog.)
            </p>
            <h5><a id="x1-6000"></a>4. Is the modality speech?</h5>
            <p>
                The present classification of spoken languages follows the existing well-established methodology for
                inferring genealogical relationships (<a
                    href="${request.route_url('source', id=94097)}">Campbell, Lyle and Poser, William J. 2008</a>).
                The relevant principles and their application are explained below in the Classification section.
            </p>
            <p>
                Since a similar methodology for the classification of sign languages remains to be formulated, 
                sign languages are classified on a weaker theoretical basis. The relevant principles and their
                application are explained below in the Classification section.
            </p>
            <h5><a id="x1-7000"></a>5. Are the form-meaning pairs enough to distinguish between different classification
                proposals?</h5>
            <p>
                We also require that the amount of form-meaning pairs is sufficient for a classification. There is no
                universal fixed threshold for how much is sufficient as this depends on how closely related the language
                is
                to other known languages. An approximate minimal requirement is 50 items or so of basic vocabulary,
                i.e.,
                not personal names or special domain vocabulary. For example, the extinct language Gamela of
                northeastern Brazil is
                known from 19 words only (<a href="${request.route_url('source', id=47776)}">Curt Nimuendajú 1937</a>:68)&mdash;hardly
                enough for a classification. It is arguable that the
                sound-values encoded in the Linear A script can be gauged, but little, if any, meaning can be inferred
                (<a href="${request.route_url('source', id=18847)}">Yves Duhoux 1998</a>, <a
                    href="${request.route_url('source', id=145800)}">Best, Jan 1989</a>, <a
                    href="${request.route_url('source', id=10744)}">K. Aartun 1997</a>), rendering the data insufficient
                for classification.
            </p>
            <p>
                If not enough form-meaning pairs are attested to allow classification, the language is filed under
                Unclassifiable.
            </p>
        </%util:section>
        <%util:section title="Classification" prefix="" level="4">
            <h5>
                <a id="x1-9000"></a>
                6. Are the form-meaning similarities to at least one other language best explained by inheritance from a
                common ancestor?
            </h5>
            <p>
                Given a language with sufficient attestation, one can compare it with the remaining languages. If there
                are
                similarities to other language(s) that can be shown exceed chance, there are three possible kinds of
                explanations: universals, contact or inheritance from a common ancestor (<a
                    href="${request.route_url('source', id=94097)}">Campbell, Lyle and Poser, William J. 2008</a>). If
                the best explanation
                for the similarities are inheritance from common ancestor, languages are classified as belonging to the
                same
                family. A language which, by this principle, does not belong to the same family as any other language is
                also
                called an isolate. What constitutes the &ldquo;best&rdquo; explanation is not a static judgment, but
                subject to change as
                new considerations and new data appear. For example, some lexical parallels between Nadahup, Kakua-Nukak
                and
                Puinave (<a href="${request.route_url('source', id=158063)}">Rivet, Paul and Constant Tastevin 1920</a>)
                were for a long time considered by many to be &ldquo;best&rdquo; explained by a genealogical
                relationship. However, thanks to increased documentation and interest in the languages, the explanation
                of
                the similarities as loans, chance resemblances and even data errors, is now favoured
                (<a href="${request.route_url('source', id=60268)}">Patience Epps 2008</a>:5-9, <a
                    href="${request.route_url('source', id=153689)}">Katherine Bolaños and Patience Epps 2009</a>, <a
                    href="${request.route_url('source', id=21440)}">Katherine Bolaños 2011</a>, <a
                    href="${request.route_url('source', id=138662)}">Girón, Jesús Mario 2008</a>:419-439). Not only the
                state of documentation and investigation
                of specific groups may alter the perceived &ldquo;best&rdquo; explanation, but also new arguments
                regarding the probative
                value of various kinds of evidence. For example, <a href="${request.route_url('source', id=21928)}">Malcolm
                Ross (1995)</a>, <a href="${request.route_url('source', id=148196)}">Malcolm Ross (2001)</a>, <a
                    href="${request.route_url('source', id=10496)}">Ross, Malcolm (2005)</a> argues that similarities
                in pronoun signatures can be used to create preliminary groupings of Papuan languages, whereas <a
                    href="${request.route_url('source', id=314563)}">Harald Hammarström (2012)</a>,
                using data from all over the world, argues that such usage of the evidence is not probative for
                genealogical
                groupings.
            </p>
            <p>
                There is the theoretical possibility that a language with sufficient attestation has simply not (yet)
                been
                compared to other relevant languages to determine if there are any non-random similarities. In practice,
                we
                know of no such language, and therefore have no separate category for languages inhabiting this logical
                possibility.
            </p>
            <p></p>
            <h5><a id="x1-10000"></a>7. Has there been sufficient comparison to determine its closest relative(s)?</h5>
            <p>
                Given a language and the other languages that belong to the same family, if insufficient data is
                available or
                insufficient comparative work has been done to determine the closest relative(s) of the language at
                hand, it
                is left unclassified within the finest-level (sub)family that can be discerned.
            </p>
            <p>
                For example, the subgrouping study of the Greater Awyu subfamily by <a
                    href="${request.route_url('source', id=304684)}">Lourens de Vries and Ruth Wester and Wilco van den
                Heuvel (2012)</a> uses shared innovations in
                verb morphology as the most reliable indicator of linguistic ancestry because, in a landscape of dialect
                chains and clan loyalty shifts (<a href="${request.route_url('source', id=305807)}">de Vries, Lourens J.
                2012</a>), lexicon and phonology is thought to be particularly vulnerable
                to diffusion. Within the Greater Awyu languages, there is a binary split between the Becking-Dawi group
                and
                the Awyu-Dumut groups. Awyu-Dumut, in turn, divides into three large dialect chains Awyu, Dumut and
                Ndeiram.
                For one language (clearly belonging to the Greater Awyu family on lexical and pronominal grounds), Sawi,
                no
                morphological data is available, so, for lack of data on verb morphology, its position within the
                subfamily
                cannot be determined and it is consequently left unclassified within it.
            </p>
            <p>
                In other cases, data availability is not the bottleneck, but the work required to ascertain the
                subgrouping.
                Plenty of data exists for Adamawa Fali and other Volta-Congo languages (although patchily distributed),
                but
                subgrouping in the Volta-Congo languages is a large and complicated issue, leaving the subgrouping of
                Adamawa Fali unresolved (<a href="${request.route_url('source', id=114627)}">Boyd, Raymond 1989</a>:180).
            </p>
            <h5><a id="x1-11000"></a>8. Is there a subgrouping based on shared innovations?</h5>
            <p>
                The preferred subgrouping criterion is a subgrouping based on shared innovations (<a
                    href="${request.route_url('source', id=98107)}">Malcolm Ross 1988</a>, <a
                    href="${request.route_url('source', id=302679)}">Malcolm Ross 1997</a>).
                For each language where such is available, that subgrouping is followed.
            </p>
            <h5><a id="x1-12000"></a>9. Are there other, weaker, arguments for subgrouping?</h5>
            <p>
                If no subgrouping based on shared innovations is available, whatever other (weaker) arguments are
                considered.
                Weaker arguments would be shared similarities in general, e.g., lexicostatistics, which may reflect
                borrowings
                and/or retentions. The subgrouping of the least bad such evidence is followed. For example, two
                independent
                published opinions exist on the internal subgrouping of the Mek languages, namely that of <a
                    href="${request.route_url('source', id=37015)}">Volker Heeschen (1978)</a>,
                <a href="${request.route_url('source', id=34449)}">Volker Heeschen (1992)</a> and that which appears in
                <a href="${request.route_url('source', id=38805)}">Peter J. Silzer and Heljä Heikkinen-Clouse (1991)</a>.
                The former gives a lexicostatistical argument for a
                subgrouping while the latter lists a subgrouping without pointing to any evidence at all. The
                lexicostatistical
                evidence is preferrable to no evidence at all, and is therefore followed.
            </p>
            <h5><a id="x1-13000"></a>On the classification of sign languages</h5>
            <p>
               The category of Sign Language languages in Glottolog is first divided
into L1 Sign Languages, Auxiliary Sign Systems and Pidgin Sign
Languages. L1 Sign Languages are full-fledged languages (in the sense
of **hh:h:Hockett:Speech**'s Design Features) that are or were
someone's mother tongue. Homesign systems, developed for basic
communication by isolated deaf children and their immediate family,
are not full-fledged languages (**hh:h:Hill:Homesign**). Homesign
systems are not catalogued in Glottolog.  A ``critical mass'' of
interacting deaf individuals can transform (a/some) homesign system
into an L1 language but precisely when this happens is a matter of
uncertainty. Perhaps a half a dozen to a dozen individuals are
sufficient and Glottolog is relatively liberal in the judgment of
particular cases. (This is visible not least in labels such as
``emergent'', ``nascent'' or ``family sign'' used in the titles of
publications about the same cases). The list of L1 sign languages in
Glottolog aims to be complete but, as with spoken languages, there has
to be a published convincing argument as to its existence and
distinctness to other languages in order to merit inclusion. Pidgin
Sign Languages, like spoken Pidgin languages, are by definition not
full-fledged languages. Although some are included, Glottolog does not
aim to be complete with respect to Pidgin Sign Languages. Auxiliary
Sign Systems are similarly, by definition, not anyone's mother tongue
(**hh:hs:Kendon:Sign-Aboriginal**):2-6, 404-441 and Glottolog does not
aim to be complete with respect to auxiliary sign systems. Deaf
individuals, like anyone else, may use an existing auxiliary sign
system and if there is ``critical mass'' of such users that may turn
the auxiliary sign system into an L1 Sign Language, e.g., Yolngu Sign
Language (**hh:s:AdoneMaypilama:Yolngu-Sign**).

The L1 Sign Languages are further classified into families, resembling
genealogical families for spoken languages. For spoken languages, a
relatively well-developed methodology, i.e., the Comparative Method
(see, e.g., **hh:hv:Weiss:Comparative-Method**), exists for
establishing relationships and subclassification. For signed
languages, such a methodology remains to be articulated (see
**hh:v:Power:Historical-Sign**:4, 9-13,
**hh:hv:Abner:Sign-Families**,
**hh:v:Wilson:French-Sign-Family**,
**hh:v:Parks:Sign-Language-Comparisons**,
**hh:hv:Reagan:Sign-Families** etc.).  In lieu of a well-developed
methodology, Glottolog sign languages are (sub-)grouped on lexical
and/or historical evidence on transmission. A lexical comparison, even
given caveats for cognacy establishment and transmission type, is
usually stronger evidence than historical evidence since a historical
connection may or may not be closely tied to the transmission of an
entire signed language. We follow earlier work that estimates that
30\% lexicostatistical similarity and above to be indicative of family
relationship (**hh:g:Hendriks:Sign-Jordanian**:37,
**hh:v:Guerra:Lexicons-Four-Signed**:228-229,
**hh:hv:McKeeKennedy:Comparison-Sign**:57-58 etc.). If lexical
evidence is not available, historical evidence, e.g., the signed
language of relevant foundational deaf institutions and/or influential
individuals therein is taken as as an indicator of the origin of a
signed language. Also evidence or arguments as to the absense of any
historical connection to other known signed language is taken as an
indicator of independent origin, i.e., a separate family/isolate.
This means that, unlike with spoken languages in Glottolog, signed
languages can be classified into families/isolates without there being
any recorded language data, i.e., form-meaning pairs. For example,
nothing has been published on lexicon or structure of the (presumed)
signed language of Dadhkai village in Jammu and Kashmir state (India).
Its existence is arguable on the incidence of deafness
(**hh:h:Razdan:Dadhkai**) and its classification as an isolate is
inferred from the lack of historical connections of this village to
any other known signed language. Also unlike spoken languages in
Glottolog, there exist signed languages for which lexical data (but
little historical information) is available, yet no systematic
comparison to neighbouring signed languages has been carried out. Such
language are listed as Unclassified L1 Sign Language is Glottolog.
For example, there is a dictionary of Rwandan Sign Language
(**hh:d:Woolley:Rwandan-Sign**) which has not been used for lexical
comparisons and the little historical information available is
insufficient to confirm or deny any relationship with deaf
schools/languages in neighbouring or far countries.

It is expected that the quality of the classification of signed
languages in Glottolog is far inferior to that of the spoken
languages. Nevertheless, unlike earlier work such as that of Anderson
(reproduced in **hh:h:Woll:Global-Sign**:27),
**hh:hv:Wittmann:Classification-Signees** or
**hh:h:Cantin:Noetomalalien**, sources are given for each
classificatory choice to enable scrutiny and facilitate future
improvement.
 
            </p>
        </%util:section>
        <%util:section title="Accountability" prefix="" level="4">
            <p>
                The outcome classification is presented in the glottolog tree. Detailed evidence that the presented
                classification
                actually conforms to the principles above is provided in the form of references to work containing or
                subsuming
                the required evidence for the decisions reflected in the classification.
            </p>
            <p>
                On the leaf level, i.e., for languages, references to actual data for each language are given,
                justifying principles 1-5.
            </p>
            <p>
                For the classification, principles 6-9, references justifying nodes are displayed in the green box below
                the
                tree-fragment box. Wherever necessary, a comment accompanies the reference if the decision reflected in
                the
                tree does not follow straightforwardly from the argumentation in the references work(s).
            </p>
            <p>
                We do not always conform to the interpretation and conventions of the authors cited as justification. It
                may be,
                for example, that an author states that a certain group should be assumed on purely geographic grounds,
                in
                anticipation of future work, or some other reason not admissible as justification in the present
                classification.
                In such cases, the justificational value of the reference is on the (lack of) evidence and/or arguments
                found
                in the reference, not necessarily the interpretation of this state given in that reference.
            </p>
            <p>
                Even though the information given in the current version of Glottolog
                is fairly substantial, we cannot guarantee that we have included all the
                relevant information yet. We decided to release Glottolog early rather
                than wait for the completed version, which will be evolving continually
                anyway.
            </p>
        </%util:section>
        <%util:section title="Names of families and subfamilies" prefix="">
            <p>
                Whenever possible, names of families and subfamilies are taken over from the current literature. This is
                considered possible when there is no name clash (with another language or (sub-)family in the world) and
                the name in the literature in principle refers to the intended set of languages. If the (sub-)family in
                the
                present classification differs in any significant way from that associated with a certain name, we have
                introduced a new unique name which is in often not found in the literature. The new names are all unique
                and unambiguous but otherwise, for the current edition of Glottolog, we spent little effort on finding
                the name optimal in describing its set
                of languages (e.g., with the name of a central river or by taking the word for &ldquo;man&rdquo;) or
                optimal in the system
                of names in the region or greater family (e.g., by using a name with a Spanish flavour if the
                surrounding
                (sub-)families have Spanish-flavoured names). A number of names may look somewhat artificial
                (e.g., Nuclear A, or, A-B-C) or out of place (e.g., a subfamily with an Anglophone name whose parent has
                a
                Francophone name), reflecting the fact that no particular value is attached to names beyond being unique
                and
                unambiguous.
            </p>
        </%util:section>
        <%util:section title="Example" prefix="">
            <p>
                For example, <a href="${request.route_url('language', id='tuca1253')}">Tucanoan</a> is a
                South American language family. <a href="${request.route_url('source', id=310719)}">Chacon, Thiago C.
                (2012)</a>, with later amendments in <a href="${request.route_url('source', id=576304)}">Ramirez, Henri.
                (2019:5-7)</a>, contains a subgrouping based on
                shared phonological innovations and defines the position in the tree for all the below nodes except
                Arapaso, Miriti, Macaguaje, Kueretu and Tama, which fall outside the scope of his study. Thus, <a
                    href="${request.route_url('source', id=310719)}">Chacon, Thiago C. (2012)</a> and <a href="${request.route_url('source', id=576304)}">Ramirez, Henri.
                (2019:5-7)</a> are given
                as the references justifying the top-level family as well as the reference justifying most intermediate
                nodes. For Western Tucanoan there's also the study by <a href="${request.route_url('source', id=557465)}">Skilton, Amalia.
                (2013)</a>, which is added to the two for that node.
                The remaining languages, Arapaso, Miriti, Macaguaje and Tama do exist (or did exist) and they are
                arguably
                Tucanoan. For Macaguaje and Tama, a small amount of data is attested and published, and this is enough
                for
                <a href="${request.route_url('source', id=56760)}">Sergio Elías Ortiz (1965:133)</a> to show that they
                are within the
                <a href="${request.route_url('language', id='sion1248')}">Siona-Secoya</a>
                group, and <a href="${request.route_url('source', id=576304)}">Ramirez, Henri.
                (2019:5-7)</a> later makes a closer assessment of their position. Thus, here <a href="${request.route_url('source', id=56760)}">Sergio Elías Ortiz (1965:133)</a>
                and <a href="${request.route_url('source', id=576304)}">Ramirez, Henri.
                (2019:5-7)</a> are cited as
                the references justifying the position of Macaguaje and Tama. For Miriti and Arapaso, <a
                    href="${request.route_url('source', id=9035)}">Brüzzi Alves da Silva, Alcionilio (1972)</a>
                was able to obtain minuscule wordlists of them which appeared in <a
                    href="${request.route_url('source', id=24652)}">Brüzzi Alves da Silva, Alcionilio (1962:96-97, 101-102)</a>,
                and concluded that they were Tucanoan but did not insist on a more specific placement himself. More recently,
                another wordlist of Arapaso collected a century earlier by Natterer has surfaced, and this allowed
                <a href="${request.route_url('source', id=576304)}">Ramirez, Henri.
                (2019:5-7)</a> to place this language more specifically to place this language more specifically in a subgroup
                with Kotiria and Wa'ikhana. Regarding Miriti, the remaining community members asserted <a
                    href="${request.route_url('source', id=24652)}">Brüzzi Alves da Silva, Alcionilio (1962:101-102)</a> that
                the language was similar to Arapaso and this is consistent with the minuscule wordlist. The language is thus classified accordingly
                with this (admittedly meagre) motivation.
            </p>
        </%util:section>
        <%util:section title="Dialects" prefix="">
            <p>
                For the current edition of Glottolog, we spent little effort on making dialect classifications
                consistent and on providing references for dialects.
                Most of the information on dialects in Glottolog is lifted from the Multitree project and contains
                numerous errors and inconsistencies which we are aware of, but have not yet had the resources to
                systematically correct.
                We hope to provide more information on dialects in the future.
            </p>
        </%util:section>
        <%util:section title="Coordinates" prefix="">
            <p>

                Glottolog provides coordinates for nearly all language-level
                languoids. The coordinate often represents the geographical
                centre-point of the area where the speakers live, but may also
                indicate a historical location, the demographic centre-point or some
                other representative point. Like (variant) names and country locations
                (but unlike language division and classification), coordinates are
                attributes close to observation and are therefore not given with a
                specific source in Glottolog. However, it is expected that any source
                attributed to the language in Glottolog would indicate a location
                compatible with the coordinate given in Glottolog. The actual sources
                for the coordinates in Glottolog are varied and include both
                individual points submitted by various users and ourselves as well as
                databases such as WALS, ASJP and human reading of Ethnologue maps. As
                such the coordinates in Glottolog are not a substitute for a full and
                well-founded source in language locations (or variant names). For
                that, one needs to look at the individual sources attributed to the
                language in Glottolog.
            </p>
        </%util:section>

        <%util:section title="Bookkeeping languoids" prefix="">
            <p>
                Glottolog contains a list of languages that the editors do not regard as real languages
                but instead as languages based on misunderstanding.
            </p>
            <p>
                Sometimes linguists claim the existence of a language that later turns out to be a misunderstanding.
                For instance, <a
                    href="${request.route_url('glottolog.languages', _query={'search': 'Yarsun'})}">Yarsun</a> was once
                claimed by Ethnologue to be an Austronesian language of northern New Guinea, and there is still an ISO
                639-3 code for it.
                However, recent research provided insufficient evidence that such a language ever existed in the sense
                of being distinct from every other language.
                In such cases, ISO 639-3 codes are often retired, because active ISO 639-3 codes must be about real
                languages.
                Glottolog never retires Glottocodes and keeps them also for bookkeeping purposes.
            </p>
        </%util:section>

        <%util:section title="Agglomerated Endangerment Status (AES)" prefix="">
            <p>
                The Agglomerated Endangerment Status (AES) is an endangerment scale, derived from the databases of
                ${h.external_link("http://www.endangeredlanguages.com", label="The Catalogue of Endangered Languages (ELCat)")}
                ,
                ${h.external_link("http://www.unesco.org/languages-atlas/", label="UNESCO Atlas of the World's Languages in Danger")}
                and
                ${h.external_link("http://www.ethnologue.com", label="Ethnologue")}. For more information see
                <a href="${req.route_url('langdocstatus')}">GlottoScope</a>, which also contains information on descriptive status.
            </p>
        </%util:section>

        <%util:section title="Acknowledgements" prefix="">
            <p>Thanks </p>
            <ul class="itemize1">
                <li class="itemize">To Hedvig Skirgård for miscellaneous corrections and issued raised</li>
                <li class="itemize">To Tim Usher for many points of dicussion re Papuan languages</li>
                <li class="itemize">To Mark Donohue for many points of dicussion re Papuan and Austronesian languages
                </li>
                <li class="itemize">To Hilário de Sousa and Andy Hsiu for many points of dicussion and clarification
                    regarding languages in the Sinosphere
                </li>
                <li class="itemize">To Matthew Dryer for many points of dicussion re Papuan and other languages</li>
                <li class="itemize">To Roger Blench for all things Nigerian and beyond</li>
                <li class="itemize">To Tom Güldemann the 'bald eagle' of African language classification</li>
                <li class="itemize">To Bonny Sands for help with access to various valuable documents</li>
                <li class="itemize">To Mikael Parkvall for help with &ldquo;Creole&rdquo; language classification</li>
                <li class="itemize">To Willem Adelaar for many points of discussion re South American languages</li>
                <li class="itemize">To Raoul Zamponi for help with access to various valuable documents</li>
                <li class="itemize">To Guillaume Segerer for help with access to various valuable documents</li>
                <li class="itemize">To all authors of descriptive and comparative works on the languages of the world
                </li>
                <li class="itemize">To 25 libraries for access and services</li>
                <li class="itemize">To over 250 individuals who provided confirming and/or clarificatory information
                </li>
            </ul>
        </%util:section>
    </div>
