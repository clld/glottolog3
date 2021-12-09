<%inherit file="glottolog3.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "about" %>

<%def name="contextnav()">
    ${util.contextnavitem('glottolog.meta', label='Languoids')}
    ${util.contextnavitem('providers', label='References')}
    ${util.contextnavitem('home.glossary', label='Glossary')}
</%def>
${next.body()}