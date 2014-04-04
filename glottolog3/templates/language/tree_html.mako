<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>

<%block name="head">
    <style>
ul.jqtree-tree .jqtree-toggler {left: 6px; width: 1em;}
ul.jqtree-tree div.jqtree-element .jqtree-title {
    margin-left: 1.5em;
}
ul.jqtree-tree a.jqtree-toggler + .jqtree-title {
    margin-left: 1.5em !important;
}
ul.jqtree-tree ul{
  list-style-type: none;
  margin-left: 0 0 0 10px;
  padding: 0;
  position: relative;
  overflow:hidden;
}

ul.jqtree-tree li{
  margin: 0;
  padding: 0 12px;
  position: relative;
}

ul.jqtree-tree li::before, ul.jqtree-tree li::after{
  content: '';
  position: absolute;
  left: 0;
}

/* horizontal line on inner list items */
ul.jqtree-tree li::before{
  border-top: 1px solid #999;
  top: 10px;
  width: 10px;
  height: 0;
}

/* vertical line on list items */
ul.jqtree-tree li:after{
  border-left: 1px solid #999;
  height: 100%;
  width: 0px;
  top: -10px;
}

/* lower line on list items from the first level because they don't have parents */
ul.jqtree-tree > li::after{
  top: 10px;
}

/* hide line from the last of the first level list items */
ul.jqtree-tree > li:last-child::after{
  display: none;
}

span.language {font-weight: bold;}
span.selected {color: orangered !important;}
    </style>
</%block>

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
