<%namespace name="util" file="../util.mako"/>

<%util:well>
    <div class="label label-info"><h5>${label|n}:</h5></div>
<%util:table items="${languages}" args="item" options="${dict(bInfo=True)}">
    <%def name="head()">
        <th>Name</th>
        <th> </th>
        <th>Most extensive description</th>
        <th>doctype</th>
        <th>pages</th>
    </%def>
    <td>${h.link(request, item[0], target='_blank')}</td>
    <td><a href="#map" onclick="CLLD.mapShowInfoWindow(null, '${item[0].id}')"><i class="icon icon-globe"> </i></a></td>
    % if item[1]:
    <td><a target="_blank" href="${request.route_url('source', id=item[1]['id'])}">${item[1]['name']}</a></td>
    <td>${item[1]['doctype']}</td>
    <td class="right">${item[1]['pages'] if item[1]['pages'] else ''}</td>
    % else:
    <td></td>
    <td></td>
    <td></td>
    % endif
</%util:table>
</%util:well>
