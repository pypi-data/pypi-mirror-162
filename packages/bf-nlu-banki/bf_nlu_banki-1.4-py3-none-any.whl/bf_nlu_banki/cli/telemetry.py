import argparse
import textwrap
from typing import List

from bf_nlu_banki import telemetry
from bf_nlu_banki.cli import SubParsersAction
import bf_nlu_banki.cli.utils
from bf_nlu_banki.shared.constants import DOCS_URL_TELEMETRY
import bf_nlu_banki.shared.utils.cli


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all telemetry tracking parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    telemetry_parser = subparsers.add_parser(
        "telemetry",
        parents=parents,
        help="Configuration of bf_nlu_banki Open Source telemetry reporting.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    telemetry_subparsers = telemetry_parser.add_subparsers()
    telemetry_disable_parser = telemetry_subparsers.add_parser(
        "disable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Disable bf_nlu_banki Open Source Telemetry reporting.",
    )
    telemetry_disable_parser.set_defaults(func=disable_telemetry)

    telemetry_enable_parser = telemetry_subparsers.add_parser(
        "enable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Enable bf_nlu_banki Open Source Telemetry reporting.",
    )
    telemetry_enable_parser.set_defaults(func=enable_telemetry)
    telemetry_parser.set_defaults(func=inform_about_telemetry)


def inform_about_telemetry(_: argparse.Namespace) -> None:
    """Inform user about telemetry tracking."""
    is_enabled = telemetry.is_telemetry_enabled()
    if is_enabled:
        bf_nlu_banki.shared.utils.cli.print_success(
            "Telemetry reporting is currently enabled for this installation."
        )
    else:
        bf_nlu_banki.shared.utils.cli.print_success(
            "Telemetry reporting is currently disabled for this installation."
        )

    print(
        textwrap.dedent(
            """
            bf_nlu_banki uses telemetry to report anonymous usage information. This information
            is essential to help improve bf_nlu_banki Open Source for all users."""
        )
    )

    if not is_enabled:
        print("\nYou can enable telemetry reporting using")
        bf_nlu_banki.shared.utils.cli.print_info("\n\tbf_nlu_banki telemetry enable")
    else:
        print("\nYou can disable telemetry reporting using:")
        bf_nlu_banki.shared.utils.cli.print_info("\n\tbf_nlu_banki telemetry disable")

    bf_nlu_banki.shared.utils.cli.print_success(
        "\nYou can find more information about telemetry reporting at "
        "" + DOCS_URL_TELEMETRY
    )


def disable_telemetry(_: argparse.Namespace) -> None:
    """Disable telemetry tracking."""
    telemetry.track_telemetry_disabled()
    telemetry.toggle_telemetry_reporting(is_enabled=False)
    bf_nlu_banki.shared.utils.cli.print_success("Disabled telemetry reporting.")


def enable_telemetry(_: argparse.Namespace) -> None:
    """Enable telemetry tracking."""
    telemetry.toggle_telemetry_reporting(is_enabled=True)
    bf_nlu_banki.shared.utils.cli.print_success("Enabled telemetry reporting.")
