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
    <ul class="inline">
    % for li in u.format_languages(request, ctx):
    ${li}
    % endfor
    </ul>
% endif
