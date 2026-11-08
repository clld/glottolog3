import json
import configparser
import urllib.request

from glottolog3.releases import Release

__all__ = ['get_releases', 'get_release']


def get_releases(args):
    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with args.pkg_dir.joinpath('releases.ini').open(encoding='utf-8') as f:
        cfg.read_file(f)
    return sorted([Release.from_config(cfg, sec) for sec in cfg.sections()])


def get_release(args, version):
    for rel in get_releases(args):
        if rel.version == version:
            return rel


def gc2version():
    with urllib.request.urlopen('https://doi.org/10.5281/zenodo.23421523') as req:
        with urllib.request.urlopen(req.url + '/files/glottocode2version.json') as r:
            return json.loads(r.read().decode('utf-8'))
