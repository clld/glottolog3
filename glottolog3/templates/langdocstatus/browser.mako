<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "glottoscope" %>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/select2.css')}" rel="stylesheet">
    <script src="${request.static_url('clld:web/static/js/select2.js')}"></script>
    <link href="${request.static_url('glottolog3:static/slider.css')}" rel="stylesheet">
    <script src="${request.static_url('glottolog3:static/bootstrap-slider.js')}"></script>
    <style type="text/css">
    .clld-map-icon {opacity: 0.7}
    </style>
</%block>

<%! from datetime import date %>
<% year, macroarea = [request.params.get(n, '') for n in 'year macroarea'.split()] %>

<%block name="title">GlottoScope</%block>

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
        <h3>GlottoScope${' - {0}'.format(' and '.join(countries.values())) if countries else ''}</h3>

        <div class="alert alert-info">
            You can investigate the documentation status for the selected languages and year
            on the
            <a class="label label-info" href="#themap">
                <i class="icon-globe icon-white"> </i>
                map
            </a>
            or view
            the
            <a class="label label-info" href="#tally">
                <i class="icon-th icon-white"> </i>
                tally
            </a>.
            A short description of GlottoScope is provided in the
            <a class="label label-info" href="${request.route_url('langdocstatus')}">
                <i class="icon-book icon-white"> </i>
                intro
            </a>.
        </div>
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
                        1500&nbsp;&nbsp;&nbsp;<input type="text" id="ys" class="big" value="" data-slider-step="1">&nbsp;&nbsp;&nbsp;${date.today().year}
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
            % if not countries:
                <tr>
                    <td>Macroarea:</td>
                    <td>
                        <select id="macroarea">
                            <option value=""${' selected="selected"' if not macroarea else ''}>any</option>
                            % for ma in macroareas.domain:
                                <option value="${ma.name}"${' selected="selected"' if macroarea == ma.name else ''}>${ma.name}</option>
                            % endfor
                        </select>
                        <input type="hidden" id="countries" value="${' '.join(countries)}"/>
                    </td>
                </tr>
                <tr>
                    <td>Family:</td>
                    <td>${families.render()}</td>
                </tr>
            % endif
            <tr>
                <td>Focus:</td>
                <td>
                    % if focus == 'sdt':
                        <i class="icon-book"></i>
                        descriptive status
                        <a class="btn btn-info" href="${u.set_focus(request.url, 'ed')}">
                            <i class="icon-heart icon-white"></i>
                            toggle
                        </a>
                    % else:
                        <i class="icon-heart"></i>
                        endangerment
                        <a class="btn btn-info" href="${u.set_focus(request.url, 'sdt')}">
                            <i class="icon-book icon-white"></i>
                            toggle
                        </a>
                    % endif
                </td>
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
        <%util:section title="Tally">
            <table id="tally" class="table table-nonfluid">
                <thead>
                <tr>
                    <th colspan="2"> </th>
                    <th colspan="3" style="text-align: left;">Language is ...</th>
                </tr>
                <tr>
                    <th> </th>
                    <th> </th>
                    % for ed, _ in endangerments:
                        <th>
                            ${ed.name.lower()}
                        </th>
                    % endfor
                    <th> </th>
                </tr>
                <tr>
                    <th colspan="2">Most extensive description is a ...</th>
                    % for ed, icon in endangerments:
                        <th style="text-align: right;">
                            <img src="${icon_map['c' + icon.color if focus != 'sdt' else icon.shape + 'ffffff']}" height="20" width="20"/>
                        </th>
                    % endfor
                    <th>total</th>
                </tr>
                </thead>
                <tbody>
                    % for i, (de, icon) in enumerate(doctypes):
                        <tr>
                            <th>${de.name}</th>
                            <th>
                                <img src="${icon_map[icon.shape + 'ffffff' if focus != 'sdt' else 'c' + icon.color]}" height="20" width="20"/>
                            </th>
                            % for ed, _ in endangerments:
                                ${stats_cell(ed.number, de.number)}
                            % endfor
                            ${stats_cell(9, de.number)}
                        </tr>
                    % endfor
                <tr>
                    <td> </td>
                    <th>total</th>
                    % for ed, _ in endangerments:
                        ${stats_cell(ed.number, 9)}
                    % endfor
                    ${stats_cell(9, 9)}
                </tr>
                </tbody>
            </table>
        </%util:section>
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

