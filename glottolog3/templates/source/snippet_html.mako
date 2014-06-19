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
<h4>Languages</h4>
<ul class="inline">
    % for lang in ctx.languages:
    <li>${h.link(request, lang)}</li>
    % endfor
</ul>
