<%inherit file="../about_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<h3>References Information</h3>

<p>
    Glottolog aims to provide complete references on the world's languages (apart
    from national languages and a few dozen other major languages for which
    thousands of studies exist).
    At the moment, it contains ${totalrefs} references on ${totalnodes}
    varieties and families. The sources of Glottolog are given below.
</p>
<p>
    Each reference is annotated for its source. In this way Glottolog gives credit
    to the creators of the resource that originally contributed the reference.
    Please help us to make Glottolog's references more complete. If you have a
    reference that is missing, or even a collection of references, please contact
    the editors. At the moment, many of Glottolog’s references are not correctly
    annotated. If you notice a reference that should be annotated differently,
    please contact the editors.
</p>

<%util:table items="${[p for p in ctx.get_query() if p.pk in ctx.ref_count]}" args="item" eid="refs" class_="table-condensed table-striped" options="${dict(aaSorting=[[3, 'desc']])}">\
    <%def name="head()">
        <th>Provider</th><th>Bibliography</th><th>Description</th><th>References</th>
    </%def>
    <td>${item.id}</td>
    <td>${h.link(request, item)}</td>
    <td><a id="provider-${item.id}" name="provider-${item.id}"> </a>${item.description or ''}</td>
    <td class="right">${ctx.ref_count[item.pk]}</td>
    <%def name="foot()">
        <th style="text-align: right;" colspan="3">Total:</th><th style="text-align: right;">${sum(ctx.ref_count.values())}</th>
    </%def>
</%util:table>
