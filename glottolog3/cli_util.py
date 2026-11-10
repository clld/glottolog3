import json
import argparse
import urllib.request

from clldutils.jsonlib import load

from glottolog3.releases import Release

__all__ = ['get_release']


def get_release(args: argparse.Namespace, version) -> Release:
    releases = load(args.pkg_dir / 'static' / 'downloads.json')
    for rel in sorted([Release.from_downloads(v, spec) for v, spec in releases.items()]):
        if rel.version == version:
            return rel
    raise ValueError(version)


def gc2version() -> dict[str, list[str]]:
    with urllib.request.urlopen('https://doi.org/10.5281/zenodo.23421523') as req:
        with urllib.request.urlopen(req.url + '/files/glottocode2version.json') as r:
            return json.loads(r.read().decode('utf-8'))
