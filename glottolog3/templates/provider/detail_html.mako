<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>

<h3>Provider ${ctx.name} ${u.github_link(ctx)}</h3>

<div class="alert alert-success">
    ${u.md(req, ctx.description)}
</div>
${request.get_datatable('sources', h.models.Source, provider=ctx).render()}
