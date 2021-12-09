<%inherit file="glottolog3.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "dataset" %>

<%def name="contextnav()">
    ${util.contextnavitem('glottolog.meta', label='About Languoids')}
    ${util.contextnavitem('providers', label='About References')}
    ${util.contextnavitem('home.glossary', label='Glossary')}
    ${util.contextnavitem('legal')}
    ${util.contextnavitem('home.downloads', label='Download')}
    ${util.contextnavitem('home.contact', label='Contact')}
</%def>
${next.body()}
