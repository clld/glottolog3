<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>


<h2>${ctx.name}</h2>

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Text</a></li>
        <li><a href="#tab2" data-toggle="tab">BibTeX</a></li>
        <li><a href="#tab3" data-toggle="tab">RIS</a></li>
        <li><a href="#tab4" data-toggle="tab">MODS</a></li>
    </ul>
    <div class="tab-content">
        <% bibrec = ctx.bibtex() %>
        <div id="tab1" class="tab-pane active">
            <p id="${h.format_gbs_identifier(ctx)}">${bibrec.text()|n}</p>
            % if ctx.datadict().get('Additional_information'):
            <p>
                ${ctx.datadict().get('Additional_information')}
            </p>
            % endif
            ${util.gbs_links(filter(None, [ctx.gbs_identifier]))}
        </div>
        <div id="tab2" class="tab-pane"><pre>${bibrec}</pre></div>
        <div id="tab3" class="tab-pane"><pre>${bibrec.format('ris')}</pre></div>
        <div id="tab4" class="tab-pane"><pre>${bibrec.format('mods')}</pre></div>
    </div>
</div>

<%def name="sidebar()">
% if ctx.doctypes:
<%util:well title="${_('Document type')}">
    <ul class="nav nav-pills nav-stacked">
    % for dt in ctx.doctypes:
        <li>
            <a href="${request.route_url('home.glossary', _anchor='doctype-' + dt.id)}">${dt.name}</a>
        </li>
    % endfor
    </ul>
</%util:well>
% endif
% if ctx.languagesource:
<%util:well title="${_('Languages')}">
    <ul class="nav nav-pills nav-stacked">
    % for source_assoc in ctx.languagesource:
        <li>${h.link(request, source_assoc.language)}</li>
    % endfor
    </ul>
</%util:well>
% endif
</%def>
