import configparser

from glottolog3.releases import Release

__all__ = ['get_releases', 'get_release']


def get_releases(args):
    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with args.pkg_dir.joinpath('releases.ini').open(encoding='utf-8') as f:
        cfg.read_file(f)
    return [Release.from_config(cfg, sec) for sec in cfg.sections()]


def get_release(args, version):
    for rel in get_releases(args):
        if rel.version == version:
            return rel
