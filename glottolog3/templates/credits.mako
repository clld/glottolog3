<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%! multirow = True %>

<div class="row-fluid">
    <div class="span10 offset1">
<h3>Credits</h3>

<div class="span6 well well-small">
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
        Cross Linguistic Linked Data project.
    </p>
    <p>
        Martin Haspelmath gave advice at every stage throughout the project, helped with
        coordination, and is currently responsible for languoid names and dialects.
    </p>
    <p>
        The table on the right gives the source bibliographies for Langdoc.
    <p>
    <img src="${request.static_url('glottolog3:static/Spitzweg.jpg')}"/>
</div>

<div class="span5">
    <%util:table items="${stats}" args="item" eid="refs" class_="table-condensed table-striped">\
        <%def name="head()">
            <th>Bibliography</th><th>References</th>
        </%def>
        <td>${h.link(request, item[0])}</td>
        <td class="right">${item[1]}</td>
        <%def name="foot()">
            <th style="text-align: right;">Total:</th><th style="text-align: right;">${sum(i[1] for i in stats)}</th>
        </%def>
    </%util:table>
</div>

    </div>
</div>
