Dear Glottolog maintainers,

% if isinstance(ctx, u.Ref):
<% bib = ctx.bibtex() %>
I found an error in reference ${ctx.id}.

It now reads
${bib}
but should read
${bib}
% elif isinstance(ctx, u.Languoid):
I found an error in languoid ${ctx.id}: ${ctx}.
% else:
I found an error in Glottolog.
% endif
