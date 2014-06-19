<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <a onclick="GLOTTOLOG3.Tree.open('kulu1253,sout2736,bodi1256')" class="button">open</a>
</%def>

<div>
    <div id="tree">
    </div>
    <script>
    $(document).ready(function() {
        var tree = $('#tree');
        tree.tree({
            autoOpen: false,
            data: ${tree|n},
            onCreateLi: function(node, $li) {
                if (node.level == 'language'){
                    $li.find('.jqtree-title').addClass('language');
                }
            }
        });
        tree.bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                document.location.href = CLLD.route_url(
                    'language', {'id': event.node.id});
            }
        );
    });
    </script>
</div>
