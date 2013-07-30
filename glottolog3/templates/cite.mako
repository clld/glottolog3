<%inherit file="home_comp.mako"/>
<% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, request.dataset, request, ext='md.txt') %>

<h3>Cite</h3>
<p>Cite this resource as:</p>
<blockquote>
    ${h.newline2br(TxtCitation.render(ctx, request))|n}
</blockquote>
<p>
    Academic publications which deal with Glottolog include:
    <ul class="unstyled">
    % for ref in refs:
        <li>
            <blockquote>
                <strong>${ref['author']}</strong> ${ref['year']}.<br>
                <em>${ref['title']}</em>.<br>
            % for attr in 'journal volume number series booktitle editor address publisher pages howpublished note isbn doi'.split():
                % if attr in ref:
                <span class="bib${attr}">${ref[attr]}</span>
                % endif
            % endfor
            % if 'url' in ref:
                <br>
                ${h.external_link(ref['url'])}
                % endif
                <br>
                <br>
                <pre>${ref}</pre>
            </blockquote>
        </li>
        % endfor
    </ul>
</p>
