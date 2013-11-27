<%inherit file="home_comp.mako"/>

<h3>Language Documentation Status</h3>

<form class="inline">
1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-min="1500" data-slider-max="2014" data-slider-step="1" data-slider-value="${year or 2014}" data-slider-selection="after" data-slider-tooltip="show">&nbsp;&nbsp;&nbsp;2014
</form>

${map.render()}

<script type="text/javascript">
    $(document).ready(function() {
        $("#ys").slider().on("slideStop", function(e) { GLOTTOLOG3.descStatsUpdateIcons(e.value); });
    });
</script>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/bootstrap-slider.js')}"></script>
</%block>
