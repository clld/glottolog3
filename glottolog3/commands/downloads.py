"""
Create downloads
"""
from glottolog3.commands import newick, geo, sqldump


def run(args):
    for cmd in [newick, geo, sqldump]:
        cmd.run(args)
