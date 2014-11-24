<%inherit file="../langdoc_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<h3>Langdoc Information</h3>

<p>
    Langdoc aims to provide complete references on the world's languages (apart
    from national languages and a few dozen other major languages for which
    thousands of studies exist).
    At the moment, it contains ${totalrefs} references on ${totalnodes}
    varieties and families. The sources of Langdoc are given below.
</p>
<p>
    Each reference is annotated for its source. In this way Langdoc gives credit
    to the creators of the resource that originally contributed the reference.
    Please help us to make Langdoc's references more complete. If you have a
    reference that is missing, or even a collection of references, please contact
    the editors. At the moment, many of Langdoc’s references are not correctly
    annotated. If you notice a reference that should be annotated differently,
    please contact the editors.
</p>

<%util:table items="${ctx.get_query()}" args="item" eid="refs" class_="table-condensed table-striped" options="${dict(aaSorting=[[2, 'desc']])}">\
    <%def name="head()">
        <th>Bibliography</th><th>Description</th><th>References</th>
    </%def>
    <td>${h.link(request, item)}</td>
    <td><a id="provider-${item.id}" name="provider-${item.id}"> </a>${item.description or ''}</td>
    <td class="right">${ctx.ref_count[item.pk]}</td>
    <%def name="foot()">
        <th style="text-align: right;" colspan="2">Total:</th><th style="text-align: right;">${sum(ctx.ref_count.values())}</th>
    </%def>
</%util:table>
