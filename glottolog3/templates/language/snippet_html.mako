<%namespace name="util" file="../util.mako"/>

<%! from clldutils import svg %>

<%def name="value(valueset)">
    <h4>${valueset.parameter.id.upper()}</h4>
    <img src="${svg.data_url(svg.icon(valueset.values[0].domainelement.jsondata['icon']))}" width="20" height="20"/>
    <strong>${valueset.values[0].name}</strong>
    (${h.linked_references(req, valueset)})
</%def>


<h3>${h.link(request, ctx)}</h3>
% if request.params.get('glottoscope'):
    ${value(ctx.valueset_dict['aes'])|n}
    ${value(ctx.valueset_dict['med'])|n}
    <p>
        ${ctx.valueset_dict['med'].references[0].source.bibtex().text()}
    </p>
    </h4>
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
