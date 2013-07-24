<%inherit file="langdoc_comp.mako"/>
<%namespace name="util" file="util.mako"/>
<%namespace name="h" file="helpers.mako"/>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/introjs.min.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/intro.min.js')}"></script>
</%block>

<h3>Complex query</h3>
<form>
<div class="span6">
    <div class="well well-small form-inline">
        <div data-step="1" data-intro="filter the tree of language families by infix"
             class="input-append">
            <input type="text" placeholder="filter tree" id="treefilter" class="input-small">
            <button class="btn" id="treefiltertrigger">filter</button>
        </div>
        <button data-step="4" data-intro="click here to trigger the reference search"
                class="btn">get references</button>
        <a class="btn btn-info" onclick="javascript:introJs().start(); return false;">Help</a>
    </div>
    <div class="span6 well well-small" style="height: 500px; overflow: scroll; margin-left: 0 !important;"
         data-step="2" data-intro="click on Family names in the tree to select them for the reference search">
            <div id="tree" data-url="${request.route_url('glottolog.childnodes')}">
            </div>
            <script>
    $(document).ready(function() {
        $('#tree').tree({
            //onCreateLi: function(node, $li) {
                // Add 'icon' span before title
            //    $li.find('.jqtree-title').before('<span class="icon"></span>');
            //}
        });
        $('#tree').bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                var label = event.node.primaryname + ' (' + event.node.alnumcode + ')',
                    selected = $('#languoids').val().split('\n'),
                    index = selected.indexOf(label);

                if (index >= 0) {
                    selected.splice(index, 1);
                } else {
                    selected.push(label);
                }
                $('#languoids').val(selected.join('\n'));
            }
        );
        $('#treefiltertrigger').click(function() {
            $('#tree').tree('loadDataFromUrl', '${request.route_url('glottolog.childnodes')}' + '?filter=' + $('#treefilter').val());
            return false;
        });
    });
            </script>
    </div>
    <div class="span6">
    <div data-step="3" data-intro="add other search criteria"
         class="accordion" id="sidebar-accordion">
        <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Languoids" open="${True}">
            <textarea rows="15" class="input-medium" id="languoids" name="languoids">${request.params.get('languoids', '')}</textarea>
        </%util:accordion_group>
        <%util:accordion_group eid="acc-area" parent="sidebar-accordion" title="Macro area">
            % for area in macroareas:
            <label><input type="checkbox" name="macroarea" value="${area.id}"${' checked' if area.id in params['macroareas'] else ''}> ${area}</label>
            % endfor
        </%util:accordion_group>
        <%util:accordion_group eid="acc-type" parent="sidebar-accordion" title="Document type">
            % for type_ in reftypes:
            <label><input type="checkbox" name="reftype" value="${type_.id}"${' checked' if type_.id in params['reftypes'] else ''}> ${type_}</label>
            % endfor
        </%util:accordion_group>
        ##<%util:accordion_group eid="acc-codes" parent="sidebar-accordion" title="Bibliographical">
        ##</%util:accordion_group>
    </div>
    </div>
</div>
</form>
<div class="span6">
    ${h.refs_table(refs)}
</div>
