<%inherit file="../glottolog3.mako"/>
<%! active_menu_item = "languages" %>

<%block name="title">${_('Languages')}</%block>

<h2>
    ${_('Languages')}
    % if country:
        of ${country.description}
        ${h.button(
            h.icon('search'),
            href=req.route_url('langdocstatus.browser',_query={'focus': 'ed', 'country': country.name}),
            title="go to GlottoScope", class_='btn-mini')}
    % endif
</h2>

${map.render()}

% if len(languages) < 2500:
<div id="list-container" class="row-fluid">
    % for langs in h.partitioned(languages, n=4):
    <div class="span3">
        <table class="table table-condensed table-nonfluid">
            <tbody>
                % for language in langs:
                <tr>
                    <% family = family_map[language.family_pk] %>
                    <% img = h.HTML.img(width='20', height='20', src=icon_map[language.family_pk]) %>
                    <td>
                        % if language.latitude is not None:
                        ${h.link_to_map(language)}
                        % endif
                    </td>
                    <td>
                        % if family:
                        ${h.link(request, family, title=family.name, rsc='language', label=img)}
                        % else:
                        ${img|n}
                        % endif
                    </td>
                    <td>${h.link(request, language)}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
    % endfor
</div>
<script>
    $(window).load(function() {
        $('.marker-toggle').click(function(e) {
            CLLD.mapToggleLanguages('${map.eid}');
            e.stopPropagation();
        });
    });
</script>
% else:
    <div class="alert alert-block">
        You selected more than 2500 languages. To display a list of language names here,
        narrow down your search.
    </div>
% endif