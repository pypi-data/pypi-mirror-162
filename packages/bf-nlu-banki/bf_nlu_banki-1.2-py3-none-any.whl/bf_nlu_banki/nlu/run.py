import asyncio
import logging
from typing import Text

from bf_nlu_banki.core.agent import Agent
from bf_nlu_banki.shared.utils.cli import print_info, print_success
from bf_nlu_banki.shared.utils.io import json_to_string

logger = logging.getLogger(__name__)


def run_cmdline(model_path: Text) -> None:
    """Loops over CLI input, passing each message to a loaded NLU model."""
    agent = Agent.load(model_path)

    print_success("NLU model loaded. Type a message and press enter to parse it.")
    while True:
        print_success("Next message:")
        try:
            message = input().strip()
        except (EOFError, KeyboardInterrupt):
            print_info("Wrapping up command line chat...")
            break

        result = asyncio.run(agent.parse_message(message))

        print(json_to_string(result))
