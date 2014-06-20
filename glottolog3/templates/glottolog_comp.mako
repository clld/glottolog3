<%inherit file="app.mako"/>
<%namespace name="u" file="util.mako"/>
<%! active_menu_item = "languages" %>

<%def name="contextnav()">
    ${u.contextnavitem('languages', label='Languages')}
    ${u.contextnavitem('glottolog.families', label='Families')}
    ${u.contextnavitem('glottolog.languages', label='Search')}
    ${u.contextnavitem('glottolog.meta', label='Languoids information')}
</%def>
${next.body()}
