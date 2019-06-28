<%inherit file="about_comp.mako"/>

<h3>Credits</h3>

<div class="span7">
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
</div>
<div class="span4 well well-small">
    <img src="${request.static_url('glottolog3:static/Spitzweg.jpg')}"/>
</div>
