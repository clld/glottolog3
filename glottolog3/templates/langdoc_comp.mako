<%inherit file="app.mako"/>
<%namespace name="u" file="util.mako"/>
<%! active_menu_item = "sources" %>

<%def name="contextnav()">
    ${u.contextnavitem('langdoc', label='Bibliographical query')}
    ${u.contextnavitem('langdoc.complexquery', label='Complex query')}
    ${u.contextnavitem('providers', label='Langdoc information')}
</%def>
${next.body()}
