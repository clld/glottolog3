<%namespace name="util" file="../util.mako"/>

<h3>${h.link(request, ctx)}</h3>
% if request.params.get('glottoscope'):
    <dl class="dl-horizontal">
        % if request.params.get('doctype'):
            <dt>Descriptive status:</dt>
            <dd>${request.params.get('doctype').replace('_', ' ')}</dd>
        % endif
        <dt>Endangerment status:</dt>
        <dd>
            ${ctx.status}
            % if request.params.get('edsrc'):
                (${request.params.get('edsrc')})
            % endif
        </dd>
    </dl>
    % if ctx.family and ctx.father:
        <h4>Classification</h4>
        <p>
            Family: ${h.link(request, ctx.family)} ...
            subgroup: ${h.link(request, ctx.father)}
        </p>
    % endif
    % if source:
        <h4>Most extensive description</h4>
        ${h.link(request, source)}
        <p>
            ${source.bibtex().text()}
        </p>
    % endif
% else:
    ${h.format_coordinates(ctx)}
% endif
