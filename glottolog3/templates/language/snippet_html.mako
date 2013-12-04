<%namespace name="util" file="../util.mako"/>

<h3>${h.link(request, ctx)}</h3>
% if source:
% if ctx.family and ctx.father:
<h4>Classification</h4>
<p>
    Family: ${h.link(request, ctx.family)} ... subgroup: ${h.link(request, ctx.father)}
</p>
% endif
<h4>Most extensive description</h4>
${h.link(request, source)}
<p>
    ${source.bibtex().text()}
</p>
% else:
${h.format_coordinates(ctx)}
% endif
