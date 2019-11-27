import configparser

from clld.scripts.util import setup_session

from glottolog3.releases import Release

__all__ = ['get_releases', 'get_release', 'with_session']


def with_session(args):
    setup_session(str(args.pkg_dir.parent.joinpath('development.ini')))


def get_releases(args):
    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with args.pkg_dir.joinpath('releases.ini').open(encoding='utf-8') as f:
        cfg.read_file(f)
    return [Release.from_config(cfg, sec) for sec in cfg.sections()]


def get_release(args, version):
    for rel in get_releases(args):
        if rel.version == version:
            return rel
