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
        marker.setIcon(map.icon(marker.feature, 20, url));
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
    var map_marker = function(node){
        return '<img src="'+node.map_marker+'" height="20" width="20">'
    };

    var marker_toggle = function(node){
        var html = '<label class="checkbox inline" style="padding-top: 0;" title="click to toggle markers">';
        html += '<input style="display: none;" type="checkbox" onclick="GLOTTOLOG3.filterMarkers(this);" ';
        html += 'class="checkbox inline" checked="checked" value="'+node.pk+'">';
        html += map_marker(node);
        html += '</label>';
        return html
    };

    return {
        init: function(eid, data, nid) {
            $('#'+eid).tree({autoOpen: false, data: data, onCreateLi: GLOTTOLOG3.Tree.node});
            if (nid){
                GLOTTOLOG3.Tree.open(eid, nid);
            }
        },
        node: function(node, li) {
            var title = li.find('.jqtree-title');
            title.addClass('level-'+node.level);
            title.html(GLOTTOLOG3.languoidLink(node));
            if (node.map_marker){
                if (node.child){
                    title.after(marker_toggle(node));
                } else {
                    title.after(map_marker(node));
                }
            }
        },
        close: function(eid) {
            var $tree = $('#' + eid);
            $tree.tree('getTree').iterate(
                function (node, level) {
                    $tree.tree('closeNode', node);
                    return true;
                }
            );
            return;
        },
        open: function(eid, nodes, scroll) {
            var el, node, top,
                $tree = $('#'+eid);

            if (!nodes) {
                $tree.tree('getTree').iterate(
                    function (node, level) {
                        if (node.level == 'dialect') {
                            return true;
                        }
                        if (!node.hasChildren()) {
                            $tree.tree('selectNode', node);
                            return false;
                        }
                        return true;
                    }
                );
                $tree.tree('selectNode', null);
                return;
            }
            nodes = nodes.split(',');
            for (var i = 0; i < nodes.length; i++) {
                node = $tree.tree('getNodeById', nodes[i]);
                el = $(node.element);
                if (top) {
                    top = Math.min(el.offset().top, top);
                } else {
                    top = el.offset().top;
                }
                el.find('span.jqtree-title').first().addClass('selected');
                $tree.tree('openNode', node);
                while (node.parent) {
                    $tree.tree('openNode', node.parent);
                    node = node.parent;
                    $(node.element).find('span.jqtree-title').first().addClass('lineage');
                }
            }
            if (top && scroll) {
                $('html, body').animate({scrollTop: top}, 500);
            }
        }
    }
})();

GLOTTOLOG3.languoidLink = function(spec){
    spec = spec === undefined ? {} : spec;
    var cls = 'Language',
        title = spec.name + ' [Glottocode: ' + spec.id + ']',
        href = CLLD.route_url('language', {'id': spec.id});
    if (spec.level == 'language' && spec.iso) {
        title += '[ISO 639-3: ' + spec.iso + ']';
    }
    if (spec.status) {
        cls += ' ' + spec.status;
        if (spec.status != 'established'){
            title += ' - ' + spec.status;
        }
    }
    return '<a href="'+href+'" class="'+cls+'" title="'+title+'">'+spec.name+'</a>';
};
