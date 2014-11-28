<%inherit file="../glottolog3.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! multirow = True %>

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

<div class="codes pull-right">
    ${util.codes()}
</div>

<h3>${ctx} ${h.contactmail(req, ctx, title='report a problem')}</h3>

${lmap.render()}
