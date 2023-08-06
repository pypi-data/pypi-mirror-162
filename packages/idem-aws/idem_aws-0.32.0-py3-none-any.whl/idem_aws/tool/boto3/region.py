def get(hub, ctx) -> str:
    """
    Get the region name from ctx and fall back to the region in config
    """
    opt = getattr(hub, "OPT") or {}
    acct = opt.get("acct") or {}
    extras = acct.get("extras") or {}
    aws_opts = extras.get("aws") or {}

    return ctx.acct.get("region_name") or aws_opts.get("region_name")
