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
        $('#tree').tree();
        $('#tree').bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                var label = event.node.lname + ' (' + event.node.glottocode + ')',
                    s = $('#select-languoid'),
                    data;
                data = s.select2('data');
                data.push({id: event.node.glottocode, text: label, level: event.node.level});
                s.select2('data', data);
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
        <fieldset>
            <legend>Languoids</legend>
            <input type="hidden" name="languoids" id="select-languoid"/>
        </fieldset>
        <fieldset>
            <legend>Macroareas</legend>
            <select name="macroareas" multiple data-placeholder="select macroarea" id="select-macroarea">
            % for area in macroareas:
            <option value="${area.id}">${area}</option>
            % endfor
            </select>
        </fieldset>
        <fieldset>
            <legend>Document types</legend>
            <select name="doctypes" multiple data-placeholder="select doctype" id="select-doctype">
            % for doctype in doctypes:
            <option value="${doctype.id}">${doctype}</option>
            % endfor
            </select>
        </fieldset>
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
<script type="text/javascript">
   $(document).ready(function() {
      $("#select-macroarea").select2({width: 'element'});
      $("#select-macroarea").select2('data', ${h.dumps([{'id': l.id, 'text': l.name} for l in params.get('macroareas', [])])|n});
      $("#select-doctype").select2({width: 'element'});
      $("#select-doctype").select2('data', ${h.dumps([{'id': l.id, 'text': l.name} for l in params.get('doctypes', [])])|n});
      $("#select-languoid").select2({
        placeholder: "Search languoid",
        minimumInputLength: 2,
        multiple: true,
        width: 'element',
        ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
            url: "${request.route_url('glottolog.childnodes')}",
            dataType: 'json',
            data: function (term, page) {
                return {
                    q: term, // search term
                    t: 'select2'
                };
            },
            results: function (data, page) { // parse the results into the format expected by Select2.
                return data;
            }
        }
      });
      $("#select-languoid").select2('data', ${h.dumps([{'id': l.id, 'text': l.name, 'level': l.level.value} for l in params.get('languoids', [])])|n});
    });
</script>
