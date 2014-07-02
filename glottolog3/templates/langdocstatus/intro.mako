<%inherit file="../langdoc_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="browser_link(label, **query)">
    <a class="label label-info"
       href="${request.route_url('langdocstatus.browser', _query=query)}"
       title="Go to Language Documentation Status Browser for ${label}">
        ${label}
    </a>
</%def>

<h3>Language Documentation Status</h3>
<p>
    The documentation status for a language is a combination of
    <a href="${request.route_url('glossary', _anchor='sec-descriptivestatusofalanguage')}">descriptive status</a>
    and vitality or endangerment status (provided by the
    <em>${unesco.description}</em>).
</p>
<p>
    The Glottolog documentation status browser allows investigation on a global level.
    Since displaying more than 7000 language locations on a map is rather taxing in terms
    of browser resources, it is advisable to only browse by macroarea. If you are confident
    that your browser has enough resources available (in particular enough memory), you may
    choose to view all languages by selecting "Any" in the macroareas control of the
    browser.
</p>
<h4>Browse status by macro area</h4>
<ul class="inline">
    % for ma in macroareas:
    <li>${browser_link(ma.name, macroarea=ma.name)}</li>
    % endfor
</ul>
<h4>Browse status by language family</h4>
<%util:table items="${families}" args="item" options="${dict(bInfo=True)}" class_="table-nonfluid table-compact">
    <%def name="head()">
        <th>Glottocode</th>
        <th>Name</th>
        <th>Child languages</th>
        <th>Macroareas</th>
    </%def>
    <td>${h.link(request, item, label=item.id)}</td>
    <td>${browser_link(item.name, family=item.id)}</td>
    <td class="right">${item.child_language_count}</td>
    <td>
        <ul class="inline">
            % for ma in item.macroareas:
            <li>${browser_link(ma.name, macroarea=ma.name)}</li>
            % endfor
        </ul>
    </td>
</%util:table>
