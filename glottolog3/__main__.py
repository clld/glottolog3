import sys
import pathlib
import argparse
import contextlib

from cldfcatalog import Config, Catalog
from clldutils.clilib import register_subcommands, get_parser_and_subparsers, ParserError
from clldutils.loglib import Logging

from pyglottolog import Glottolog

import glottolog3
import glottolog3.commands


def main(args=None, catch_all=False, parsed_args=None, log=None):
    try:
        repos = Config.from_file().get_clone('glottolog')
    except KeyError:  # pragma: no cover
        repos = pathlib.Path('.')
    parser, subparsers = get_parser_and_subparsers('glottolog3')
    parser.add_argument(
        '--repos',
        help="clone of glottolog/glottolog",
        default=repos,
        type=pathlib.Path)
    parser.add_argument(
        '--repos-version',
        help="version of repository data. Requires a git clone!",
        default=None)
    parser.add_argument(
        '--pkg-dir',
        help=argparse.SUPPRESS,
        default=pathlib.Path(__file__).parent)
    register_subcommands(subparsers, glottolog3.commands)

    args = parsed_args or parser.parse_args(args=args)

    if not hasattr(args, "main"):  # pragma: no cover
        parser.print_help()
        return 1

    with contextlib.ExitStack() as stack:
        if not log:  # pragma: no cover
            stack.enter_context(Logging(args.log, level=args.log_level))
        else:
            args.log = log
        if args.repos_version:  # pragma: no cover
            # If a specific version of the data is to be used, we make
            # use of a Catalog as context manager:
            stack.enter_context(Catalog(args.repos, tag=args.repos_version))
        args.repos = Glottolog(args.repos)
        args.log.info('glottolog/glottolog at {0}'.format(args.repos.repos))
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except ParserError as e:  # pragma: no cover
            print(e)
            return main([args._command, '-h'])
        except Exception as e:  # pragma: no cover
            if catch_all:
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
