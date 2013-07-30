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
