<%inherit file="home_comp.mako"/>

<h3>Language Documentation Status <span id="year">${request.params.get('year', '')}</span></h3>

<form class="form-inline">
1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-min="1500" data-slider-max="2014" data-slider-step="1" data-slider-value="${request.params.get('year', '2014')}" data-slider-selection="after" data-slider-tooltip="hide">&nbsp;&nbsp;&nbsp;2014
<label style="margin-left: 2em;"><input type="checkbox" id="extinct_mode" /> Mark extinct languages</label>
</form>

${map.render()}

<div class="row-fluid">
    <div class="span5">
        <table class="table table-nonfluid">
            <thead>
                <tr>
                    <th>Most extensive description is ...</th>
                    <th colspan="3" style="text-align: center;">Languages</th>
                </tr>
                <tr>
                    <th> </th>
                    <th>living</th>
                    <th>extinct</th>
                    <th>total</th>
                </tr>
            </thead>
            <tbody>
        % for label, type in [('grammar', 'grammar'), ('sketch', 'sketch'), ('dictionary', 'dictionary'), ('other', 'other')]:
                <tr>
                    <th>a ${label}</th>
                    % for subtype in ['living', 'extinct', 'total']:
                    <% _type = '-'.join([type, subtype]) %>
                    <td><a title="click to open list of languages" onclick="GLOTTOLOG3.descStatsLoadLanguages('${_type}')" id="${_type}"> </a></td>
                    % endfor
                </tr>
        % endfor
            </tbody>
        </table>
    </div>

    <div id="languages" class="span7"> </div>
</div>

<script type="text/javascript">
    $(document).ready(function() {
        $("#ys").slider().on("slideStop", function(e) {
            $('#year').text(e.value);
            GLOTTOLOG3.descStatsUpdateIcons();
        });
        $("#extinct_mode").change(function() {
            GLOTTOLOG3.descStatsUpdateIcons();
        });
        % if request.params.get('extinct_mode'):
        $("#extinct_mode").prop('checked', true);
        % endif
    });
</script>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/bootstrap-slider.js')}"></script>
</%block>
