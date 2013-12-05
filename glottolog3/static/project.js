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
GLOTTOLOG3.descStatsUpdateIcons = function(map) {
    var extinct_mode = $('#extinct_mode').prop('checked'),
        stats = {
            'grammar': [0, 0],
            'sketch': [0, 0],
            'dictionary': [0, 0],
            'other': [0, 0]},
        color_map = {
            '006400': 'grammar',
            '00ff00': 'grammar',
            'd3d3d3': 'sketch',
            'ff8040': 'sketch',
            '708a90': 'dictionary',
            'ff4500': 'dictionary',
            '000000': 'other',
            'ff0000': 'other'},
        year = $("#year").text();
    if (year) {
        year = parseInt(year);
    }
    map = map === undefined ? CLLD.Maps['map'] : map;
    map.eachMarker(function(marker){
        // update marker icon and source id used for info query
        var i, source, url;

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
                        break;
                    }
                }
            }
        } else {
            // no year given, base properties on the global MED
            url = marker.feature.properties.icon;
            if (extinct_mode) {
                url = marker.feature.properties.eicon;
            }
            if (marker.feature.properties.med) {
                marker.feature.properties.info_query = {'source': marker.feature.properties.med};
            }
        }

        try {
            stats[color_map[url]][marker.feature.properties.extinct ? 1 : 0] += 1;
        } catch (e) {
            alert(url);
        }

        //alert(CLLD.url('/static/icons/c000000.png'));
        marker.setIcon(map.icon(marker.feature, 20, CLLD.url('/static/icons/c' + url + '.png')));
    });

    for (type in stats) {
        if (stats.hasOwnProperty(type)) {
            $('#' + type + '-living').text(stats[type][0]);
            $('#' + type + '-extinct').text(stats[type][1]);
            $('#' + type + '-total').text(stats[type][0] + stats[type][1]);
        }
    }
};
GLOTTOLOG3.descStatsLoadLanguages = function(type) {
    $("#languages" ).load("desc_stats/" + type + "?year=" + $("#year").text() + "&macroarea=" + $("#macroarea").text());
};
