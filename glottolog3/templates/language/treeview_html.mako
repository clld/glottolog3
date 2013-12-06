<%inherit file="../glottolog_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%block name="title">${ctx}</%block>

<%block name="head">
    <script src="${request.static_url('clld:web/static/js/raphael.min.js')}"></script>
    <script src="${request.static_url('clld:web/static/js/jsphylosvg.min.js')}"></script>
</%block>

<ul class="nav nav-pills pull-right">
    <li class="active">
        <a href="#" id="download-link">Tree as SVG</a>
    </li>
    <li class="active">
        <a href="${request.resource_url(ctx, ext='phylo.xml')}">Tree as PhyloXML</a>
    </li>
</ul>

<h3>Language classification rooted at ${ctx.name}</h3>
<p>
    Mouse-over the names of the leaves to see the intermediate subgroups.
</p>

% if ctx.child_language_count >= 350:
<div class="alert alert-info">
    ${ctx.name} has more than 500 child languages. For performance reasons the tree below
    does only list the first 3 levels of subgroups.
</div>
% endif

<div id="svgCanvas"> </div>
<script type="text/javascript">
    $(document).ready(function(){
        Smits.PhyloCanvas.Render.Parameters.Rectangular.alignRight = true;
        Smits.PhyloCanvas.Render.Parameters.Rectangular.alignPadding = 250;
        Smits.PhyloCanvas.Render.Parameters.Rectangular.bufferX = 500;
        Smits.PhyloCanvas.Render.Parameters.Rectangular.minHeightBetweenLeaves = 5;
        Smits.PhyloCanvas.Render.Style.text["font-size"] = 16;
        Smits.PhyloCanvas.Render.Style.text["font-family"] = 'Helvetica';
        //$.get("${request.static_url('glottolog3:static/trees/tree-' + ctx.id + '-phylo.xml')}", function(data) {
        $.get("${request.resource_url(ctx, ext='phylo.xml')}", function(data) {
            var dataObject = {
                xml: data,
                fileSource: true
            };
            phylocanvas = new Smits.PhyloCanvas(
                dataObject,
                'svgCanvas',
                1000, ${ctx.child_language_count * 35 if ctx.child_language_count < 350 else 1500}//,
                //'circular'
            );

            var svgSource = phylocanvas.getSvgSource();
            if(svgSource){
                $('#download-link')[0].href = "data:image/svg+xml," + encodeURIComponent(svgSource);
            }
        });
    });
</script>
