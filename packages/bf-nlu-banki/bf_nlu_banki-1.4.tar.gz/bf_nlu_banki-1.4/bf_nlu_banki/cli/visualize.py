import argparse
import os
from typing import List

from bf_nlu_banki.cli import SubParsersAction
from bf_nlu_banki.cli.arguments import visualize as arguments
from bf_nlu_banki.shared.constants import DEFAULT_DATA_PATH


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all visualization parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    visualize_parser = subparsers.add_parser(
        "visualize",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Visualize stories.",
    )
    visualize_parser.set_defaults(func=visualize_stories)

    arguments.set_visualize_stories_arguments(visualize_parser)


def visualize_stories(args: argparse.Namespace) -> None:
    import bf_nlu_banki.core.visualize

    args.stories = bf_nlu_banki.shared.data.get_core_directory(args.stories)
    if args.nlu is None and os.path.exists(DEFAULT_DATA_PATH):
        args.nlu = bf_nlu_banki.shared.data.get_nlu_directory(DEFAULT_DATA_PATH)

    bf_nlu_banki.core.visualize.visualize(
        args.domain, args.stories, args.nlu, args.out, args.max_history
    )
