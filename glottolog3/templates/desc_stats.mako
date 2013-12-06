<%inherit file="home_comp.mako"/>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
    <link href="${request.static_url('clld:web/static/css/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/bootstrap-slider.js')}"></script>
</%block>

<% year, macroarea = [request.params.get(n, '') for n in 'year macroarea'.split()] %>

<div class="row-fluid">
    <div class="span8">
<h3>Language Documentation Status</h3>
<form class="form-inline">
1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-min="1500" data-slider-max="2014" data-slider-step="1" data-slider-value="${request.params.get('year', '2014') or '2014'}" data-slider-selection="after" data-slider-tooltip="hide">&nbsp;&nbsp;&nbsp;2014
<label style="margin-left: 2em;"><input type="checkbox" id="extinct_mode" /> Mark extinct languages</label>
</form>
    </div>
    <div class="span4 well well-small">
        <table class="table">
            <tr><td>Year:</td><td><span id="year">${year}</span></td></tr>
            <tr>
                <td>Macroarea:</td>
                <td>
                    <select id="macroarea">
                        <option value=""${' selected="selected"' if not macroarea else ''}>any</option>
                        % for ma in macroareas:
                        <option value="${ma.name}"${' selected="selected"' if macroarea == ma.name else ''}>${ma.name}</option>
                        % endfor
                    </select>
                </td>
            </tr>
            <tr>
                <td>Family:</td>
                <td>${families.render()}</td>
                ##<td>${h.link(request, family) if family else ''} <span style="display: none;" id="family">${family.id if family else ''}</span></td>
            </tr>
        </table>
    </div>
</div>

<div class="row-fluid">
    <div class="span12">
${map.render()}
    </div>
</div>

<div class="row-fluid">
    <div class="span5">
        <table class="table table-nonfluid">
            <thead>
                <tr>
                    <th>Most extensive description is a ...</th>
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
        % for i, sdt in enumerate(doctypes):
                <tr>
                    <th>${sdt.name}</th>
                    % for type in ['living', 'extinct', 'total']:
                    <td>
                        <a style="cursor: pointer;"
                           title="click to open list of languages"
                           onclick="GLOTTOLOG3.descStatsLoadLanguages('${type}', ${i})" id="${type}-${i}"> </a>
                    </td>
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
            GLOTTOLOG3.descStatsUpdate();
        });
        $("#extinct_mode").change(function() {
            GLOTTOLOG3.descStatsUpdate();
        });
        $("#macroarea").change(function() {
            document.location.href = CLLD.route_url(
                'desc_stats', {}, {'macroarea': $("#macroarea").val(), 'year': $('#year').text(), 'family': $('#msfamily').select2('val').join()});
        });
        % if request.params.get('extinct_mode'):
        $("#extinct_mode").prop('checked', true);
        % endif
        $("#msfamily").on("change", function(e) {
            document.location.href = CLLD.route_url(
                'desc_stats', {}, {'macroarea': $("#macroarea").val(), 'year': $('#year').text(), 'family': $('#msfamily').select2('val').join()});
        })
    });
</script>
