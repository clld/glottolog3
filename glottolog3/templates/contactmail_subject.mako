% if isinstance(ctx, u.Ref):
Error in Glottolog reference ${ctx.id}
% elif isinstance(ctx, u.Languoid):
Error in Glottolog languoid ${ctx.id}
% else:
Error in Glottolog
% endif
