<%inherit file="app.mako"/>
<%! active_menu_item = None %>
<%block name="brand">
  <a class="brand" href="${request.route_url('dataset')}" title="${request.dataset.name}">
      <img src="${request.static_url('glottolog3:static/glottolog_logo.png')}" width="28"/>
      Glottolog
  </a>
</%block>
<%block name="navextra">
  <div class="pull-right">
    <form class="navbar-form form-search" role="search" action="${request.route_url('glottolog.languages')}">
      <div class="input-append">
        <input tabindex="1" type="text" class="search-query input-medium" placeholder="pr. Name / glcode / iso" name="search" id="site-search-input">
        <button tabindex="2" id="site-search-button" class="btn" type="submit"><i class="icon-search"></i></button>
      </div>
    </form>
  </div>
</%block>
${next.body()}
