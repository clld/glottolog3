<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! multirow = True %>

<%block name="title">${ctx}</%block>

<%block name="head">
    <link  rel="alternate" type="application/rdf+xml" href="${request.resource_url(ctx, ext='rdf')}" title="Structured Descriptor Document (RDF/XML format)"/>
    <link  rel="alternate" type="text/n3" href="${request.resource_url(ctx, ext='n3')}" title="Structured Descriptor Document (n3 format)"/>
</%block>

<% level = 'Subfamily' if ctx.level.value == 'family' and ctx.father_pk else ctx.level.value.title() %>
<div class="row-fluid">
    <div class="span8">
        <div style="float: right; margin-top: 20px;">${h.alt_representations(req, ctx, doc_position='left', exclude=['bigmap.html', 'snippet.html'])|n}</div>
        <h3>
            ${level}: <span class="level-${ctx.level.value}">${ctx}</span>
            ${h.contactmail(req, ctx, title='report a problem')}
            ${u.github_link(ctx)}
        </h3>
        <div class="well well-small" style="overflow: visible;">
            <ul class="inline pull-right">
                <li>${h.button(h.icon('screenshot', inverted=True), 'open ' + ctx.name, title="open current node", onclick="GLOTTOLOG3.Tree.open('tree', '"+ctx.id+"', true)", class_='btn-info btn-mini')}</li>
                <li>${h.button(h.icon('resize-full', inverted=True), 'expand all', title="expand all nodes", onclick="GLOTTOLOG3.Tree.open('tree')", class_='btn-info btn-mini')}</li>
                <li>${h.button(h.icon('resize-small', inverted=True), 'collapse all', title="collapse all nodes", onclick="GLOTTOLOG3.Tree.close('tree')", class_='btn-info btn-mini')}</li>
            </ul>
            <h4 style="margin-top: 0;">
                Classification
                <a href="${request.route_url('glottolog.meta', _anchor='classification')}">${h.icon('question-sign')}</a>
            </h4>
            <div id="tree">
            </div>

            % if ctx._crefs('fc'):
                <h5 title="The references cited contain or further point down to arguments for including exactly the set of languages here deemed to belong to the family.">
                    Family membership references
                </h5>
                ${u.format_justifications(request, ctx._crefs('fc'))}
            % endif
            % if ctx.fc:
                <h5>Comments on family membership</h5>
                <p>${u.md(request, ctx.fc.description)}</p>
            % endif
            % if ctx.screfs:
                <h5 title="${u'The references cited contain arguments for the placement of the node {0} with respect to its parents or the subclassification of the daughters of {0}.'.format(ctx.name)}">
                    Subclassification references
                </h5>
                ${u.format_justifications(request, ctx.screfs)}
            % endif
            % if ctx.sc:
                <h5>Comments on subclassification</h5>
                <p>${u.md(request, ctx.sc.description)}</p>
            % endif

        </div>
        <script>
    $(document).ready(function() {
        GLOTTOLOG3.Tree.init('tree', ${h.dumps(ctx.jqtree(icon_map))|n}, '${ctx.id}');
    });
        </script>
        % if ctx.family and ctx.family.name == 'Bookkeeping':
        <div class="alert">
            This entry has been retired and is featured here only for bookkeeping purposes. Either
            the entry has been replaced with one or more more accurate entries or it has been retired
            because it was based on a misunderstanding to begin with.
        </div>
        % endif
        % if ctx.ethnologue_comment:
            ${u.format_ethnologue_comment(req, ctx)|n}
        % endif
        % if ctx.iso_retirement:
            ${u.format_iso_retirement(req, ctx)|n}
        % endif
    </div>

    <div class="span4">
        <div class="codes pull-right">
            ${util.codes()}
        </div>
        <div class="accordion" id="sidebar-accordion" style="margin-top: 1em; clear: right;">
            <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
                ${lmap.render()}
                ${h.button('show big map', href=request.resource_url(ctx, ext='bigmap.html'))}
            </%util:accordion_group>
            % if ctx.countries:
            <%util:accordion_group eid="acc-countries" parent="sidebar-accordion" title="Countries">
                <ul class="nav nav-tabs nav-stacked">
                    % for country in ctx.countries:
                        <li>
                            <a href="${request.route_url('glottolog.languages', _query=dict(country=country.id))}">
                                ${country} [${country.id}]
                            </a>
                        </li>
                    % endfor
                </ul>
            </%util:accordion_group>
            % endif
            <% sites = [s for s in request.registry.settings.get('PARTNERSITES', []) if s['condition'](ctx)] %>
            % if sites:
            <%util:accordion_group eid="acc-partner" parent="sidebar-accordion" title="Links" open="${map is None}">
                <ul class="nav nav-tabs nav-stacked">
                % for site in sites:
                    <% hrefs = site['hrefs'](ctx) if 'hrefs' in site else [site['href'](ctx)] %>
                    % for href in hrefs:
                        <li>
                            <a href="${href}" target="_blank" title="${site['name']}">
                                % if 'logo' in site:
                                <img src="${request.static_url('glottolog3:static/%s' % site['logo'])}" alt="${site['name']}" height="20px" width="20px"/>
                                % endif
                                ${site['name']}
                            </a>
                        </li>
                    % endfor
                % endfor
                </ul>
            </%util:accordion_group>
            % endif
            <% altnames = [i for i in ctx.identifiers if i.type == 'name' and (i.description != ctx.GLOTTOLOG_NAME or i.name != ctx.name)] %>
            % if altnames or ('name_comment' in ctx.datadict()):
            <%util:accordion_group eid="acc-names" parent="sidebar-accordion" title="Alternative names">
                % if 'name_comment' in ctx.datadict():
                <p>${u.format_comment(request, ctx.datadict()['name_comment'])}</p>
                % endif
                <dl>
                % for provider, names in h.groupby(sorted(altnames, key=lambda n: n.description), lambda j: j.description):
                    <dt>${provider}:</dt>
                    % for name in names:
                    <dd>
                        ${name.name}
                        % if provider == 'lexvo' and name.lang:
                        [${name.lang}]
                        % endif
                    </dd>
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
