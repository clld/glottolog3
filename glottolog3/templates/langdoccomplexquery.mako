<%inherit file="langdoc_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/introjs.min.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/intro.min.js')}"></script>
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
</%block>

<h3>Complex query</h3>
<form>
<div class="span6">
    <div class="span6 well well-small form-inline">
        <div data-step="1" data-intro="filter the tree of language families by infix"
             class="input-append">
            <input type="text" placeholder="filter tree" id="treefilter" class="input-small">
            <button class="btn" id="treefiltertrigger">filter</button>
        </div>
    </div>
    <div class="span6 well well-small form-inline">
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
        $('#tree').tree();
        $('#tree').bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                CLLD.MultiSelect.addItem(
                    'mslanguoids',
                    {
                        id: event.node.glottocode,
                        text: event.node.lname,
                        level: event.node.level
                    }
                );
            }
        );
        $('#treefiltertrigger').click(function() {
            $('#tree').tree('loadDataFromUrl', '${request.route_url('glottolog.childnodes')}' + '?q=' + $('#treefilter').val());
            return false;
        });
    });
            </script>
    </div>
    <div class="span6" data-step="3" data-intro="add other search criteria">
        % for name in ['languoids', 'macroareas', 'doctypes']:
        <fieldset>
            <legend>${name.capitalize()}</legend>
            ${ms[name].render(params.get(name))}
        </fieldset>
        % endfor
        <fieldset>
            <legend>Bibliographical data</legend>
            % for name, value in params['biblio'].items():
            <input name="${name}"
                   value="${value}"
                   placeholder="${name.capitalize()}"
                   class="input-block-level"
                   type="text">
            % endfor
        </fieldset>
    </div>
</div>
</form>
<div class="span6">
    % if dt:
    ${dt.render()}
    % endif
</div>
