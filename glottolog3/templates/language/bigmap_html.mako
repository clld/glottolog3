<%inherit file="../glottolog_comp.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! multirow = True %>

<% request.map.icon_map = icon_map %>
<%block name="title">${ctx}</%block>

<%block name="head">
    <link  rel="alternate" type="application/rdf+xml" href="${request.resource_url(ctx, ext='rdf')}" title="Structured Descriptor Document (RDF/XML format)"/>
    <link  rel="alternate" type="text/n3" href="${request.resource_url(ctx, ext='n3')}" title="Structured Descriptor Document (n3 format)"/>
</%block>

<ul class="breadcrumb">
    % for l in reversed(list(ctx.get_ancestors())):
    <li>${h.link(request, l)} <span class="divider">/</span></li>
    % endfor
    <li class="active">${h.link(request, ctx)}</li>
</ul>

<h3>${ctx} ${h.contactmail(req, ctx, title='report a problem')}</h3>

<div class="codes pull-right">
    <span class="label label-info">Glottocode: ${ctx.id}</span>
    % if ctx.iso_code:
    <span class="large label label-info">ISO 639-3: ${h.external_link('http://www.sil.org/iso639-3/documentation.asp?id=' + ctx.iso_code, inverted=True, label=ctx.iso_code, style="color: white;")}</span>
    % endif
</div>

${request.map.render()}
