<%inherit file="../glottolog_comp.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! multirow = True %>

<% request.map.icon_map = icon_map %>
<%block name="title">${ctx}</%block>

<%block name="head">
    <link  rel="alternate" type="application/rdf+xml" href="${request.resource_url(ctx, ext='rdf')}" title="Structured Descriptor Document (RDF/XML format)"/>
    <link  rel="alternate" type="text/n3" href="${request.resource_url(ctx, ext='n3')}" title="Structured Descriptor Document (n3 format)"/>
</%block>

<%def name="nodes(tree, level)">
    <% item = tree[level] %>
    <ul>
        <li>
            <%util:tree_node_label level="${str(level)}" id="tn${str(item.id)}">
                % if item == ctx:
                    ${u.languoid_link(request, ctx, active=False, classification=True)}
                    % if request.map and ctx.latitude:
                    <img src="${request.map.icon_map[ctx.pk]}" height="20" width="20">
                    % endif
                % else:
                ${u.languoid_link(request, item, classification=True)}
                % endif
            </%util:tree_node_label>

            % if len(tree) > level + 1:
            ${nodes(tree, level + 1)}
            % endif
            % if item == ctx:
            <ul>
                % for child in filter(lambda c: not (ctx.level.value == 'family' and c.level.value == 'dialect'), ctx.children):
                <li>
                    ${u.languoid_link(request, child, classification=True)}
                    % if child.level.value != 'dialect' and map:
                    <label class="checkbox inline" title="click to toggle markers">
                        <input type="checkbox" onclick="GLOTTOLOG3.filterMarkers(this);" class="checkbox inline" checked="checked" value="${child.pk}">
                        <img src="${request.map.icon_map[child.pk]}" height="20" width="20">
                    </label>
                    % endif
                </li>
                % endfor
            </ul>
            % endif
        </li>
        % if len(tree) == level + 1:
            % for sibling in filter(lambda s: s != ctx and not (ctx.father.level.value == 'family' and s.level.value == 'dialect'), ctx.father.children if ctx.father else []):
            <li>${u.languoid_link(request, sibling, classification=True)}</li>
            % endfor
        % endif
    </ul>
</%def>

<div class="row-fluid">
    <div class="span8">
        <h3>${ctx} ${h.contactmail(req, ctx, title='report a problem')}</h3>
        % if ctx.active:
        <div class="treeview well well-small">
            ${nodes(list(reversed([ctx] + list(ctx.get_ancestors()))), 0)}
        </div>
        <script>
        $(document).ready(function() {
            CLLD.TreeView.init();
        });
        </script>
        % else:
        <div class="alert">
            <h4>Superseded Languoid</h4>
            <p>
                This languoid is no longer part of the Glottolog classification.
            </p>
            <% repl = list(ctx.get_replacements()) %>
            % if repl:
            <p>You may want to look at the following languoids for relevant information.</p>
            % endif
            <ul>
                % for l, r in repl:
                <li>${u.languoid_link(request, l)}${' [' + r + ']' if r else ''}</li>
                % endfor
            </ul>
        </div>
        % endif

        % if ctx.status and ctx.status != u.LanguoidStatus.established:
        <div class="alert">
            This language is ${ctx.status}.
        </div>
        % endif

        % if ctx.fc or ctx.sc or ctx.crefs:
        <div class="alert alert-success">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <h4>Classification</h4>
            % if ctx.fc:
            <p>${u.format_classificationcomment(request, ctx.fc.description)}</p>
            % endif
            % if ctx.sc:
            <p>${u.format_classificationcomment(request, ctx.sc.description)}</p>
            % endif
            % if ctx.crefs:
            <h5>References</h5>
            ${u.format_justifications(request, ctx.crefs)}
            % endif
        </div>
        % endif
    </div>

    <div class="span4">
        <div class="codes pull-right">
            <span class="label label-info">Glottocode: ${ctx.id}</span>
            % if ctx.iso_code:
            <span class="large label label-info">ISO 639-3: ${h.external_link('http://www.sil.org/iso639-3/documentation.asp?id=' + ctx.iso_code, inverted=True, label=ctx.iso_code, style="color: white;")}</span>
            % endif
        </div>
        <div class="accordion" id="sidebar-accordion" style="margin-top: 1em; clear: right;">
            % if request.map:
            <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
                ${request.map.render()}
                ${h.button('show big map', href=request.resource_url(ctx, ext='bigmap.html'))}
            </%util:accordion_group>
            % endif
            <% sites = filter(lambda s: s['condition'](ctx), request.registry.settings.get('PARTNERSITES', [])) %>
            % if sites:
            <%util:accordion_group eid="acc-partner" parent="sidebar-accordion" title="Links" open="${map is None}">
                <ul class="nav nav-tabs nav-stacked">
                % for site in sites:
                    <li>
                        <a href="${site['href'](ctx)}" target="_blank" title="${site['name']}">
                            % if 'logo' in site:
                            <img src="${request.static_url('glottolog3:static/%s' % site['logo'])}" alt="${site['name']}" height="20px" width="20px"/>
                            % endif
                            ${site['name']}
                        </a>
                    </li>
                % endfor
                </ul>
            </%util:accordion_group>
            % endif
            <% altnames = filter(lambda i: i.type == 'name' and i.description != 'Glottolog', ctx.identifiers) %>
            % if altnames:
            <%util:accordion_group eid="acc-names" parent="sidebar-accordion" title="Alternative names">
                <dl>
                % for provider, names in h.groupby(sorted(altnames, key=lambda n: n.description), lambda j: j.description):
                    <dt>${provider}:</dt>
                    % for name in names:
                    <dd>${name.name}</dd>
                    % endfor
                % endfor
                </dl>
            </%util:accordion_group>
            % endif
        </div>
    </div>
</div>

<div class="row-fluid">
    <div class="span12">
    <h4>References</h4>
% if ctx.child_language_count < 500:
    ${request.get_datatable('sources', h.models.Source, language=ctx).render()}
% else:
    <div class="alert alert-block">
        This family has more than 500 languages. Please select an appropriate sub-family to get a list of relevant references.
    </div>
% endif
    </div>
</div>
