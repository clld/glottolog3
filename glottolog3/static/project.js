GLOTTOLOG3 = {}
GLOTTOLOG3.filterMarkers = function(ctrl) {
    ctrl = $(ctrl);
    CLLD.mapFilterMarkers('map', function(marker){
        return (marker.feature.properties.branch != ctrl.val() && marker._icon.style.display != 'none') || (marker.feature.properties.branch == ctrl.val() && ctrl.prop('checked'));
    });
};

GLOTTOLOG3.formatLanguoid = function (obj) {
    return '<span class="level-' + obj.level + '">' + obj.text + '</span>';
};

/**
 *
 */
GLOTTOLOG3.Slider = (function(){
    var slider,
        min = 1500.0,
        max = new Date().getFullYear();

    return {
        increment: function(howmuch){
            var value = slider.slider('getValue');
            if (howmuch < 0) {
                value = Math.max(value + howmuch, min);
            } else {
                value = Math.min(value + howmuch, max);
            }
            slider.slider('setValue', value, true);
        },
        init: function(value){
            if (value == 0) {
                value = max;
            }
            slider = $('#ys');
            slider.slider({min: min, max: max, tooltip: 'hide'});
            slider.slider().on("slideStop", function(e) {
                $('#year').val(e.value);
                GLOTTOLOG3.LangdocStatus.update();
            });
            slider.slider().on("slide", function(e) {
                $('#year').val(e.value);
                GLOTTOLOG3.LangdocStatus.update();
            });
            slider.slider('setValue', value, true);
        }
    }
})();

GLOTTOLOG3.LangdocStatus = (function(){
    return {
        toggleMarkers:  function() {
            CLLD.mapFilterMarkers('map', function(marker){
                var checkbox = $('#marker-toggle-ed-' + marker.feature.properties.ed);
                return checkbox.length && checkbox.prop('checked');
            })
        },
        loadLanguages: function(ed, sdt) {
            var url = CLLD.route_url(
                'langdocstatus.languages',
                {'ed': ed, 'sdt': sdt},
                {
                    'macroarea': $("#macroarea").val(),
                    'year': $('#year').val(),
                    'family': $("#msfamily").select2("val").join()
                });
            $("#languages").focus().load(url);
        },
        reload: function(){
            document.location.href = CLLD.route_url(
                'langdocstatus.browser',
                {},
                {
                    'macroarea': $("#macroarea").val(),
                    'year': $('#year').val(),
                    'family': $('#msfamily').select2('val').join()
                }
            );
        },
        update: function(){
            var j, k, total,
                stats = [
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0]
                ],
                totals = [0, 0, 0, 0, 0, 0],
                year = $("#year").val(),
                map = CLLD.Maps['map'];

            if (!map) {
                return;
            }

            if (year) {
                year = parseInt(year);
            }
            map.eachMarker(function(marker){
                // update marker icon and source id used for info query
                var i, source, url, sdt = 3;

                if (year) {
                    // set the defaults:
                    url = marker.feature.properties.red_icon;
                    marker.feature.properties.info_query = {};

                    if (marker.feature.properties.sources) {
                        // try to find a source respecting the cut-off year
                        for (i = 0; i < marker.feature.properties.sources.length; i++) {
                            source = marker.feature.properties.sources[i];
                            if (source.year <= year) {
                                url = source.icon;
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
                    if (marker.feature.properties.med) {
                        marker.feature.properties.info_query = {'source': marker.feature.properties.med};
                    }
                }

                stats[sdt][marker.feature.properties.ed] += 1;
                marker.setIcon(map.icon(marker.feature, 20, url));
            });
            // update the stats table:
            for (j = 0; j < stats.length; j++) {
                total = 0;
                for (k = 0; k < stats[j].length; k++) {
                    $('#cell-' + k + '-' + j).text(stats[j][k]);
                    total += stats[j][k];
                    totals[k] += stats[j][k];
                }
                $('#cell-total-' + j).text(total);
            }
            total = 0;
            for (j = 0; j < totals.length; j++) {
                $('#cell-' + j + '-total').text(totals[j]);
                total += totals[j];
            }
            $('#cell-total-total').text(total);
        }
    }
})();

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
