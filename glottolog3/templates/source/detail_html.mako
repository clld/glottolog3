<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>


<h3>${ctx.name}  ${h.contactmail(req, ctx, title='report a problem')}</h3>
##<abbr class="unapi-id" title="${h.urlescape(request.resource_url(ctx))}"></abbr>
${ctx.coins(request)|n}

% if ctx.jsondatadict.get('thanks'):
<div class="alert alert-info">
    This record was contributed by ${ctx.jsondatadict['thanks']}.
</div>
% endif

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
            % if ctx.url:
            <p>
                ${h.external_link(ctx.url)}
            </p>
            % endif
            ${util.gbs_links(filter(None, [ctx.gbs_identifier]))}
            % if ctx.jsondatadict.get('internetarchive_id'):
                <hr />
                <iframe src='https://archive.org/stream/${ctx.jsondatadict.get('internetarchive_id')}?ui=embed#mode/1up' width='680px' height='750px' frameborder='1' ></iframe>
            % endif
         </div>
        <div id="tab2" class="tab-pane"><pre>${bibrec}</pre></div>
        <div id="tab3" class="tab-pane"><pre>${bibrec.format('ris')}</pre></div>
        <div id="tab4" class="tab-pane"><pre>${bibrec.format('mods')}</pre></div>
    </div>
</div>

<%def name="sidebar()">
% if ctx.doctypes:
<%util:well>
    <h3>Document types${u.format_ca_icon(req, ctx, 'doctype')}</h3>
    <ul class="inline">
    % for dt in ctx.doctypes:
        <li>
            ${u.format_label_link(request.route_url('home.glossary', _anchor='doctype-' + dt.id), dt.name.capitalize().replace('_', ' '), title=dt.description)}
        </li>
    % endfor
    </ul>
</%util:well>
% endif
% if ctx.languages:
<%util:well>
    ${u.format_language_header(request, ctx, level=3)}
    <ul class="unstyled">
    % for li in u.format_languages(request, ctx):
    ${li}
    % endfor
    </ul>
</%util:well>
% endif
<%util:well>
    <h3>Providers</h3>
    <ul class="inline">
    % for p in ctx.providers:
        <li>
            ${u.format_label_link(request.resource_url(p), p.name, title=p.description)}
        </li>
    % endfor
    </ul>
</%util:well>
</%def>
