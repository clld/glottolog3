<%inherit file="langdoc_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<h3>Bibliographical query</h3>
<div class="span4 well well-small">
    <form>
        <fieldset>
            % for name, label in param_spec:
            <input name="${name}"${' value="'+params[name]+'"' if params[name] else ''|n}
                   placeholder="${label}"
                   class="input-block-level"
                   type="text">
            % endfor
            <button type="submit" class="btn">Submit</button>
        </fieldset>
    </form>
</div>
<div class="span7">
    ##${h.refs_table(u.getRefs(**params) if filter(None, params.values()) else (0, []))}
</div>
