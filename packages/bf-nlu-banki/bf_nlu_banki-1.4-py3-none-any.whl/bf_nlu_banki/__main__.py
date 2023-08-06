import argparse
import logging
import os
import platform
import sys

from rasa_sdk import __version__ as rasa_sdk_version
from bf_nlu_banki.constants import MINIMUM_COMPATIBLE_VERSION

import bf_nlu_banki.telemetry
import bf_nlu_banki.utils.io
import bf_nlu_banki.utils.tensorflow.environment as tf_env
from bf_nlu_banki import version
from bf_nlu_banki.cli import (
    data,
    export,
    interactive,
    run,
    scaffold,
    shell,
    telemetry,
    test,
    train,
    visualize,
    x,
    evaluate,
)
from bf_nlu_banki.cli.arguments.default_arguments import add_logging_options
from bf_nlu_banki.cli.utils import parse_last_positional_argument_as_model_path
from bf_nlu_banki.shared.exceptions import bf_nlu_bankiException
from bf_nlu_banki.shared.utils.cli import print_error
from bf_nlu_banki.utils.common import configure_logging_and_warnings

logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Parse all the command line arguments for the training script."""

    parser = argparse.ArgumentParser(
        prog="bf_nlu_banki",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="bf_nlu_banki command line interface. bf_nlu_banki allows you to build "
        "your own conversational assistants 🤖. The 'bf_nlu_banki' command "
        "allows you to easily run most common commands like "
        "creating a new bot, training or evaluating models.",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Print installed bf_nlu_banki version",
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
    add_logging_options(parent_parser)
    parent_parsers = [parent_parser]

    subparsers = parser.add_subparsers(help="bf_nlu_banki commands")

    scaffold.add_subparser(subparsers, parents=parent_parsers)
    run.add_subparser(subparsers, parents=parent_parsers)
    shell.add_subparser(subparsers, parents=parent_parsers)
    train.add_subparser(subparsers, parents=parent_parsers)
    interactive.add_subparser(subparsers, parents=parent_parsers)
    telemetry.add_subparser(subparsers, parents=parent_parsers)
    test.add_subparser(subparsers, parents=parent_parsers)
    visualize.add_subparser(subparsers, parents=parent_parsers)
    data.add_subparser(subparsers, parents=parent_parsers)
    export.add_subparser(subparsers, parents=parent_parsers)
    x.add_subparser(subparsers, parents=parent_parsers)
    evaluate.add_subparser(subparsers, parents=parent_parsers)

    return parser


def print_version() -> None:
    """Prints version information of bf_nlu_banki tooling and python."""

    try:
        from bf_nlu_bankix.community.version import __version__

        bf_nlu_banki_x_info = __version__
    except ModuleNotFoundError:
        bf_nlu_banki_x_info = None

    print(f"bf_nlu_banki Version      :         {version.__version__}")
    print(f"Minimum Compatible Version: {MINIMUM_COMPATIBLE_VERSION}")
    print(f"bf_nlu_banki SDK Version  :         {rasa_sdk_version}")
    print(f"bf_nlu_banki X Version    :         {bf_nlu_banki_x_info}")
    print(f"Python Version    :         {platform.python_version()}")
    print(f"Operating System  :         {platform.platform()}")
    print(f"Python Path       :         {sys.executable}")


def main() -> None:
    """Run as standalone python application."""
    parse_last_positional_argument_as_model_path()
    arg_parser = create_argument_parser()
    cmdline_arguments = arg_parser.parse_args()

    log_level = getattr(cmdline_arguments, "loglevel", None)
    configure_logging_and_warnings(
        log_level, warn_only_once=True, filter_repeated_logs=True
    )

    tf_env.setup_tf_environment()
    tf_env.check_deterministic_ops()

    # insert current path in syspath so custom modules are found
    sys.path.insert(1, os.getcwd())

    try:
        if hasattr(cmdline_arguments, "func"):
            bf_nlu_banki.utils.io.configure_colored_logging(log_level)
            bf_nlu_banki.telemetry.initialize_telemetry()
            bf_nlu_banki.telemetry.initialize_error_reporting()
            cmdline_arguments.func(cmdline_arguments)
        elif hasattr(cmdline_arguments, "version"):
            print_version()
        else:
            # user has not provided a subcommand, let's print the help
            logger.error("No command specified.")
            arg_parser.print_help()
            sys.exit(1)
    except bf_nlu_bankiException as e:
        # these are exceptions we expect to happen (e.g. invalid training data format)
        # it doesn't make sense to print a stacktrace for these if we are not in
        # debug mode
        logger.debug("Failed to run CLI command due to an exception.", exc_info=e)
        print_error(f"{e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
