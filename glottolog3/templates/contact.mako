<%inherit file="home_comp.mako"/>

<h3>Contact ${h.contactmail(req, None, title='report a problem')}</h3>
    <div class="well">
        <p>You can contact us via email at <a href="mailto:${request.dataset.contact}">${request.dataset.contact}</a>.
        We are happy to receive additional bibliographies in any format, and feedback of any sort.</p>
        % if request.registry.settings.get('clld.github_repos') and request.registry.settings.get('clld.github_repos_data'):
        <% srepo = request.registry.settings['clld.github_repos'] %>
        <% drepo = request.registry.settings['clld.github_repos_data'] %>
        <p><a href="https://github.com">GitHub</a> users can also create and discuss bug reports using the following <strong>issue trackers</strong>:
        <ul>
            <li><a href="https://github.com/${drepo}/issues">${drepo}/issues</a> for errata on languoids &amp; references</li>
            <li><a href="https://github.com/${srepo}/issues">${srepo}/issues</a> for problems with the site software</li>
        </ul>
        % endif
    </div>
