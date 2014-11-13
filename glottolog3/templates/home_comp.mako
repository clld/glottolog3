<%inherit file="glottolog3.mako"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "dataset" %>

<%def name="contextnav()">
    ${util.contextnavitem('legal')}
    ##${util.contextnavitem('download')}
    ${util.contextnavitem('home.glossary', label='Glossary')}
    ${util.contextnavitem('home.cite', label='Cite')}
    ${util.contextnavitem('home.credits', label='Credits')}
    ${util.contextnavitem('home.downloads', label='Linked Data')}
    ${util.contextnavitem('home.contact', label='Contact')}
</%def>
${next.body()}
