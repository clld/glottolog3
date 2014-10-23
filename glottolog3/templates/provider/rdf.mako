<%inherit file="../resource_rdf.mako"/>
<%block name="properties">
    % if ctx.url:
    <dcterms:source>${ctx.url}</dcterms:source>
    % endif
</%block>
