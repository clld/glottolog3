<%inherit file="../glottolog_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<h3>Choose by property</h3>
<div class="span4 well well-small">
    <form>
        % if request.admin:
        <input type="hidden" name="__admin__" value="1"/>
        % endif
        <fieldset>
            <legend>Name</legend>
            <input type="text" name="name" id="inputName" placeholder="Name" value="${'' if message else params['name']}">
            <label class="radio">
                <input type="radio" name="namequerytype" value="whole" ${'checked' if params['namequerytype'] == 'whole' else ''}>
                match whole name
            </label>
            <label class="radio">
                <input type="radio" name="namequerytype" value="part" ${'checked' if params['namequerytype'] == 'part' else ''}>
                match part of name
            </label>
            <label class="checkbox">
                <input type="checkbox" name="multilingual" ${'checked' if params['multilingual'] else ''}> include non-English names
            </label>
            <button type="submit" class="btn">Submit</button>
        </fieldset>
    </form>
    <form>
        <fieldset>
            <legend>ISO 639-3</legend>
            <div class="input-append">
                <input class="input-small" type="text" name="iso" id="inputIso" value="${'' if message else params['iso']}" placeholder="abc">
                <button type="submit" class="btn">Submit</button>
            </div>
        </fieldset>
    </form>
    <form>
        <fieldset>
            <legend>Glottocode</legend>
            <div class="input-append">
                <input class="input-small" type="text" name="alnum" id="inputAlnum" placeholder="abcd1234">
                <button type="submit" class="btn">Submit</button>
            </div>
        </fieldset>
    </form>
    <form>
        <fieldset>
            <legend>Country</legend>
            <div class="input-append">
                <input type="text" name="country" data-provide="typeahead" data-source="${countries}" placeholder="DE">
                <button class="btn" type="submit">Submit</button>
            </div>
        </fieldset>
    </form>
</div>
<div class="span7">
    % if map:
    <div class="accordion" id="sidebar-accordion" style="margin-top: 1em;">
        <%util:accordion_group eid="acc-map" parent="sidebar-accordion" title="Map" open="${True}">
            ${map.render()}
        </%util:accordion_group>
    </div>
    % endif
    % if message:
    <div class="alert alert-error"><p>${message}</p></div>
    % else:
    <%util:table items="${languoids}" args="item" class_="table-condensed table-striped">\
        <%def name="head()">
            <th>Glottocode</th>
            <th>Name</th>
            ##<th>Type</th>
            ##<th>Status</th>
            <th>Family</th>
        </%def>
        <td>${h.link(request, item, label=item.id)}</td>
        <td class="level-${item.level.value}">${h.link(request, item)}</td>
        ##<td>${item.level}</td>
        ##<td>${item.status or ''}</td>
        <td>${u.languoid_link(request, item.family) if item.family else ''}</td>
        ##<td>${', '.join(n.name for n in item.identifiers if n.type == 'iso639-3')}</td>
    </%util:table>
    % endif
</div>
