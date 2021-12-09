<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

<textarea class="input-block-level" id="md-${ctx.pk}">${ctx.bibtex().text()}</textarea>
<script>
$(document).ready(function() {
    $("#md-${ctx.pk}").focus(function() {
        var $this = $(this);
        $this.select();

        // Work around Chrome's little problem
        $this.mouseup(function() {
            // Prevent further mouseup intervention
            $this.unbind("mouseup");
            return false;
        });
    });
    $("#md-${ctx.pk}").focus();
});
</script>
% if ctx.languages:
    ${u.format_language_header(request, ctx, level=4)}
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
% endif
