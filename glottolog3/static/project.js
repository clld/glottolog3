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
        marker.setIcon(map.icon(marker.feature, 20, url));
    });
};
