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
                    % if item.level == 'dialect':
                    <em>${item}</em>
                    % elif item.level == 'language':
                    <strong>${item}</strong>
                    % else:
                    ${item}
                    % endif
                    % if request.map and ctx.latitude:
                    <img src="${request.map.icon_map[ctx.pk]}" height="20" width="20">
                    % endif
                % else:
                ${h.link(request, item)}
                % endif
            </%util:tree_node_label>

            % if len(tree) > level + 1:
            ${nodes(tree, level + 1)}
            % endif
            % if item == ctx:
            <ul>
                % for child in ctx.children:
                <li>
                    ${h.link(request, child)}
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
            % for sibling in filter(lambda s: s != ctx, ctx.father.children if ctx.father else []):
            <li>${h.link(request, sibling)}</li>
            % endfor
        % endif
    </ul>
</%def>

<div class="row-fluid">
    <div class="span8">
        <h3>${ctx}</h3>
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
            <h4>Superseeded Languoid</h4>
            <p>
                This languoid is no longer part of the Glottolog classification.
            </p>
            <ul>
                % for l, r in ctx.get_replacements():
                <li>${h.link(request, l)} [${r}]</li>
                % endfor
            </ul>
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
        % for code in filter(lambda c: c.type == h.models.IdentifierType.iso.value, ctx.identifiers):
            <span class="large label label-info">ISO 639-3: ${h.external_link('http://www.sil.org/iso639-3/documentation.asp?id=' + code.id, inverted=True, label=code.id, style="color: white;")}</span>
        % endfor
        </div>
        <div class="accordion" id="sidebar-accordion" style="margin-top: 1em; clear: right;">
            % if request.map:
            <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
                ${request.map.render()}
                ##    <a class="btn btn-info" href="${request.route_url('glottolog.languoid_bigmap', id=ctx.alnumcode)}">show big map</a>
                <p>Coordinates: ${ctx.latitude}, ${ctx.longitude}</p>
            </%util:accordion_group>
            % endif
            <%util:accordion_group eid="acc-partner" parent="sidebar-accordion" title="Links" open="${map is None}">
                <ul class="nav nav-tabs nav-stacked">
                % for site in request.registry.settings.get('PARTNERSITES', []):
                    % if site['condition'](ctx):
                    <li>
                        <a href="${site['href'](ctx)}" target="_blank" title="${site['name']}">
                            % if 'logo' in site:
                            <img src="${request.static_url('glottolog3:static/%s' % site['logo'])}" alt="${site['name']}" height="20px" width="20px"/>
                            % endif
                            ${site['name']}
                        </a>
                    </li>
                    % endif
                % endfor
                </ul>
            </%util:accordion_group>
            <%util:accordion_group eid="acc-names" parent="sidebar-accordion" title="Alternative names">
                <dl>
                % for provider, names in h.groupby(sorted(filter(lambda i: i.type == 'name', ctx.identifiers), key=lambda n: n.description), lambda j: j.description):
                    <dt>${provider}:</dt>
                    % for name in names:
                    <dd>${name.name}</dd>
                    % endfor
                % endfor
                </dl>
            </%util:accordion_group>
        </div>
    </div>
</div>

% if ctx.sources:
<div class="row-fluid">
    <div class="span12">
    <h4>References</h4>
    ${request.get_datatable('sources', h.models.Source, language=ctx).render()}
    </div>
</div>
% endif
