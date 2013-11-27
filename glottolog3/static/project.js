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
GLOTTOLOG3.descStatsUpdateIcons = function(year) {
    var map = CLLD.Maps['map'],
        size = $('input[name=iconsize]:checked').val();
    map.eachMarker(function(marker){
        var i, source, url = marker.feature.properties.red_icon;
        marker.feature.properties.info_query = {};
        if (marker.feature.properties.sources) {
            for (i = 0; i < marker.feature.properties.sources.length; i++) {
                source = marker.feature.properties.sources[i];  // [type, year, id, url]
                if (source[1] && source[1] <= year) {
                    url = source[3];
                    marker.feature.properties.info_query = {'source': source[2]};
                    break;
                }
            }
        }
        marker.setIcon(map.icon(marker.feature, size, url));
    });
};
