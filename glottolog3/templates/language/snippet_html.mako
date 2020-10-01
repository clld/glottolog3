<%namespace name="util" file="../util.mako"/>

<%! from clldutils import svg %>

<%def name="value(valueset)">
    <h4>${valueset.parameter.id.upper()}</h4>
    <img src="${svg.data_url(svg.icon(valueset.values[0].domainelement.jsondata['icon']))}" width="20" height="20"/>
    <strong>${valueset.values[0].name}</strong>
    % if request.params.get('edsrc') == 'Glottolog':
        (Glottolog)
    % else:
        (${h.linked_references(req, valueset)})
    % endif
</%def>


<h3>${h.link(request, ctx)}</h3>
% if request.params.get('glottoscope'):
    ${value(ctx.valueset_dict['aes'])|n}
    % if request.params.get('year'):
        <h4>MED (before ${request.params.get('year')})</h4>
        % if request.params.get('source'):
            <% src = h.models.Source.get(request.params['source']) %>
            <% de = h.models.DomainElement.get('med-' + request.params['med_type']) %>
            <img src="${svg.data_url(svg.icon(de.jsondata['icon']))}" width="20" height="20"/>
            <strong>${de.name}</strong>
            (${h.link(request, src)})
            <p>
                ${src.bibtex().text()}
            </p>
        % else:
            None
        % endif
    % else:
    ${value(ctx.valueset_dict['med'])|n}
    <p>
        ${ctx.valueset_dict['med'].references[0].source.bibtex().text()}
    </p>
    % endif
    % if ctx.family and ctx.father:
        <h4>Classification</h4>
        <p>
            Family: ${h.link(request, ctx.family)} ...
            subgroup: ${h.link(request, ctx.father)}
        </p>
    % endif
% else:
    ${h.format_coordinates(ctx)}
% endif
