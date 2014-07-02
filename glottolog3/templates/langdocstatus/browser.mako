<%inherit file="../langdoc_comp.mako"/>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
    <link href="${request.static_url('clld:web/static/css/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/bootstrap-slider.js')}"></script>
</%block>

<% year, macroarea = [request.params.get(n, '') for n in 'year macroarea'.split()] %>

<%def name="stats_cell(ed, sdt)">
    <td class="right">
        <a style="cursor: pointer;"
           title="click to open list of languages"
           onclick="GLOTTOLOG3.LangdocStatus.loadLanguages(${ed}, ${sdt})"
           id="cell-${'total' if ed == 9 else ed}-${'total' if sdt == 9 else sdt}"> </a>
    </td>
</%def>

<div class="row-fluid">
    <div class="span8">
        <h3>Language Documentation Status Browser</h3>
<form class="form-inline">
1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-min="1500" data-slider-max="2014" data-slider-step="1" data-slider-value="${request.params.get('year', '2014') or '2014'}" data-slider-selection="after" data-slider-tooltip="hide">&nbsp;&nbsp;&nbsp;2014
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
    <div class="span12">
        <table class="table table-nonfluid">
            <thead>
                <tr>
                    <th colspan="2"> </th>
                    <th colspan="3" style="text-align: left;">Language is ...</th>
                </tr>
                <tr>
                    <th> </th>
                    <th> </th>
                    % for ed in endangerments:
                        <th>
                            ${ed.name.lower()}
                        </th>
                    % endfor
                    <th> </th>
                </tr>
                <tr>
                    <th colspan="2">Most extensive description is a ...</th>
                    % for ed in endangerments:
                        <th style="text-align: right;">
                            <img src="${icon_map[ed.shape + 'ffffff']}" height="20" width="20"/>
                        </th>
                    % endfor
                    <th>total</th>
                </tr>
            </thead>
            <tbody>
        % for i, sdt in enumerate(doctypes):
                <tr>
                    <th>${sdt.name}</th>
                    <th>
                        <img src="${icon_map['c' + sdt.color]}" height="20" width="20"/>
                    </th>
                    % for ed in endangerments:
                        ${stats_cell(ed.ord, i)}
                    % endfor
                    ${stats_cell(9, i)}
                </tr>
        % endfor
                <tr>
                    <td> </td>
                    <th>total</th>
                    % for ed in endangerments:
                    ${stats_cell(ed.ord, 9)}
                    % endfor
                    ${stats_cell(9, 9)}
                </tr>
            </tbody>
        </table>
    </div>
</div>

<div class="row-fluid">
    <div class="span12" id="languages">
    </div>
</div>

<script type="text/javascript">
    $(document).ready(function() {
        $("#ys").slider().on("slideStop", function(e) {
            $('#year').text(e.value);
            GLOTTOLOG3.LangdocStatus.update();
        });
        $("#macroarea").change(GLOTTOLOG3.LangdocStatus.reload);
        $("#msfamily").on("change", GLOTTOLOG3.LangdocStatus.reload);
    });
</script>
