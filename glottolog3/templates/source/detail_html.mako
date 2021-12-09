<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>
<%! multirow = True %>
<%! from itertools import groupby %>


<%block name="title">${ctx.name}</%block>

<div class="row-fluid">
    <div class="span7">

        <h3>${ctx.name}  ${h.contactmail(req, ctx, title='report a problem')}</h3>
        ##<abbr class="unapi-id" title="${h.urlescape(request.resource_url(ctx))}"></abbr>
${ctx.coins(request)|n}

        % if ctx.jsondata.get('thanks'):
            <div class="alert alert-success">
                This record was contributed by ${ctx.jsondata['thanks']}.
            </div>
        % endif

        <div class="tabbable">
            <ul class="nav nav-tabs">
                <li class="active"><a href="#tab1" data-toggle="tab">Text</a></li>
                <li><a href="#tab2" data-toggle="tab">BibTeX</a></li>
            </ul>
            <div class="tab-content">
                <% bibrec = ctx.bibtex() %>
                <div id="tab1" class="tab-pane active">
                    <p id="${h.format_gbs_identifier(ctx)}">${bibrec.text()}</p>
                    % if ctx.datadict().get('Additional_information'):
                        <p>
                            ${ctx.datadict().get('Additional_information')}
                        </p>
                    % endif
                    <ul class="inline">
                        % if ctx.author == 'ISO 639-3 Registration Authority':
                            <li>${u.format_external_link_in_label(ctx.howpublished, 'ISO 639-3')}</li>
                        % endif
                        % if ctx.url:
                            <li>${u.format_external_link_in_label(ctx.url)}</li>
                        % elif ctx.jsondata.get('doi'):
                            <li>${u.format_external_link_in_label('http://dx.doi.org/%s' % ctx.jsondata['doi'], 'DOI')}</li>
                        % endif
                        % if ctx.gbid:
                            <li>${u.format_external_link_in_label('https://books.google.com/books?id=%s' % ctx.gbid.split('id=')[-1], label='Google Books')}</li>
                        % endif
                        <% oclc = ctx.jsondata.get('oclc') %>
                        % if oclc:
                            <li>${u.format_external_link_in_label('http://www.worldcat.org/oclc/{0}'.format(oclc), 'WorldCat')}</li>
                        % endif
                        ##<% isbn = ctx.jsondata.get('isbn') %>
                ##% if isbn:
                ##    ${util.gbs_links(['ISBN:{0}'.format(isbn)])}
                ##% endif
            </ul>
                    % if ctx.iaid:
                        <hr/>
                        <iframe src='https://archive.org/stream/${ctx.iaid}?ui=embed#mode/1up' width='680px'
                                height='750px' frameborder='1'></iframe>
                    % endif
                </div>
                <div id="tab2" class="tab-pane">
                    <pre>${bibrec}</pre>
                </div>
            </div>
        </div>
    </div>

    <div class="span5">

        % if ctx.doctypes:
            <%util:well>
                <h3>Document types${u.format_ca_icon(req, ctx, 'doctype')}</h3>
                <ul class="inline">
                    % for dt in ctx.doctypes:
                        <li>
                            ${u.format_label_link(request.route_url('home.glossary', _anchor='doctype-' + dt.id), dt.name.capitalize().replace('_', ' '), title=dt.description)}
                        </li>
                    % endfor
                </ul>
            </%util:well>
        % endif
        % if ctx.languages:
            <%util:well>
            ${u.format_language_header(request, ctx, level=3)}
                <table class="table table-condensed">
                <thead>
                <tr>
                    <th>Name in source</th>
                    <th>Glottolog languoid</th>
                </tr>
                </thead>
                <tbody>
                    % for names, links in u.format_languages(request, ctx):
                    <tr>
                        <td>${names}</td>
                        <td>${links}</td>
                    </tr>
                    % endfor

                </tbody>
                </table>
            </%util:well>
        % endif
        <%util:well>
            <h3>Providers</h3>
            <ul class="inline">
                % for p, keys in groupby(ctx.bibkeys, lambda bk: bk.provider):
                    <dl>
                        <dt>${h.link(request, p)}</dt>
                        % for k in keys:
                            <dd><a href="${request.route_url('source', id=k.id)}">${k.id}</a></dd>
                        % endfor
                    </dl>
                % endfor
            </ul>
        </%util:well>
    </div>
</div>
