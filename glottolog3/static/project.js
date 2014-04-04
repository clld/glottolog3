GLOTTOLOG3 = {}
GLOTTOLOG3.filterMarkers = function(ctrl) {
    ctrl = $(ctrl);
    CLLD.mapFilterMarkers('map', function(marker){
        return (marker.feature.properties.branch != ctrl.val() && marker._icon.style.display != 'none') || (marker.feature.properties.branch == ctrl.val() && ctrl.prop('checked'));
    });
}
GLOTTOLOG3.formatLanguoid = function (obj) {
    return '<span class="level-' + obj.level + '">' + obj.text + '</span>';
}
GLOTTOLOG3.descStatsUpdate = function(map) {
    var extinct_mode = $('#extinct_mode').prop('checked'),
        stats = [[0, 0], [0, 0], [0, 0], [0, 0]],
        year = $("#year").text(),
        j;
    if (year) {
        year = parseInt(year);
    }
    map = map === undefined ? CLLD.Maps['map'] : map;
    map.eachMarker(function(marker){
        // update marker icon and source id used for info query
        var i, source, url, sdt = 3;

        if (year) {
            // set the defaults:
            url = marker.feature.properties.red_icon;
            if (extinct_mode) {
                url = marker.feature.properties.red_eicon;
            }
            marker.feature.properties.info_query = {};

            if (marker.feature.properties.sources) {
                // try to find a source respecting the cut-off year
                for (i = 0; i < marker.feature.properties.sources.length; i++) {
                    source = marker.feature.properties.sources[i];
                    if (source.year <= year) {
                        url = extinct_mode ? source.eicon : source.icon;
                        marker.feature.properties.info_query = {'source': source.id};
                        sdt = source.sdt;
                        break;
                    }
                }
            }
        } else {
            // no year given, base properties on the global MED
            url = marker.feature.properties.icon;
            sdt = marker.feature.properties.sdt;
            if (extinct_mode) {
                url = marker.feature.properties.eicon;
            }
            if (marker.feature.properties.med) {
                marker.feature.properties.info_query = {'source': marker.feature.properties.med};
            }
        }

        stats[sdt][marker.feature.properties.extinct ? 1 : 0] += 1;
        //alert(CLLD.url('/static/icons/c000000.png'));
        marker.setIcon(map.icon(marker.feature, 20, CLLD.url('/static/icons/c' + url + '.png')));
    });

    for (j = 0; j < stats.length; j++) {
        $('#living-' + j).text(stats[j][0]);
        $('#extinct-' + j).text(stats[j][1]);
        $('#total-' + j).text(stats[j][0] + stats[j][1]);
    }
};
GLOTTOLOG3.descStatsLoadLanguages = function(type, index) {
    var url = CLLD.route_url(
        'desc_stats_languages',
        {'type': type, 'index': index},
        {'macroarea': $("#macroarea").val(), 'year': $('#year').text(), 'family': $("#msfamily").select2("val").join()});
    $("#languages").load(url);
};

GLOTTOLOG3.Tree = (function(){
    return {
        open: function(nodes) {
            var el, node, top,
                $tree = $('#tree');
            nodes = nodes.split(',');
            for (var i = 0; i < nodes.length; i++) {
                node = $tree.tree('getNodeById', nodes[i]);
                el = $(node.element);
                if (top) {
                    top = Math.min(el.offset().top, top);
                } else {
                    top = el.offset().top;
                }
                el.find('span.jqtree-title').addClass('selected');
                el.css('border-color', 'red !important');
                while (node.parent) {
                    $tree.tree('openNode', node.parent);
                    node = node.parent;
                    $(node.element).css('border-color', 'red !important');
                    //$(node.element).find('.jqtree-title').addClass('selected');
                }
            }
            if (top) {
                $('html, body').animate({scrollTop: top}, 2000);
            }
        }
    }
})();