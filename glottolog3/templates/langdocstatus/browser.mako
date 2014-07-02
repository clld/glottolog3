<%inherit file="../langdoc_comp.mako"/>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
    <link href="${request.static_url('glottolog3:static/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('glottolog3:static/bootstrap-slider.js')}"></script>
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

<%def name="increment(amount)">
    <button href="#" onclick="GLOTTOLOG3.Slider.increment(${amount})" class="btn">${'+' if amount > 0 else ''}${amount}</button>
</%def>

<div class="row-fluid">
    <div class="span6">
        <h3>Language Documentation Status Browser</h3>
        <p>
            You can investigate the documentation status for the selected languages and year
            on the <a class="label label-info" href="#themap">map</a> or view
            the <a class="label label-info" href="#tally">tally</a>.
        </p>
    </div>
    <div class="span6">
        <div style="margin-top: 10px;" class="well well-small">
        <table class="table">
            <thead>
            <tr>
                <td>Year:</td>
                <td>
                    <input class="input-mini" disabled="disabled" type="text" id="year" value="${year}"/>
                    <br/>
                    ##<form class="form-inline">
                        1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-step="1">&nbsp;&nbsp;&nbsp;2014
                    ##</form>
                    <div class="btn-toolbar">
                        <div class="btn-group">
                            ${increment(-100)}
                    ${increment(-10)}
                    ${increment(-1)}
                        </div>
                        <div class="btn-group">
                            ${increment(1)}
                    ${increment(10)}
                    ${increment(100)}
                        </div>
                    </div>
                </td>
            </tr>
            </thead>
            <tbody>
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
            </tbody>
        </table>
        </div>
    </div>
</div>

<div class="row-fluid">
    <div id="themap" class="span12">
        ${map.render()}
    </div>
</div>

<div class="row-fluid">
    <div class="span12">
        <table id="tally" class="table table-nonfluid">
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
        GLOTTOLOG3.Slider.init(${request.params.get('year', 0)});
        $("#macroarea").change(GLOTTOLOG3.LangdocStatus.reload);
        $("#msfamily").on("change", GLOTTOLOG3.LangdocStatus.reload);
    });
</script>
