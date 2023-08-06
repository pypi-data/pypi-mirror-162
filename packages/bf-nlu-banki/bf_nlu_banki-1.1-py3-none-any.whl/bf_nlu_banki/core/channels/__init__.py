from typing import Text, Dict, List, Type

from bf_nlu_banki.core.channels.channel import (  # noqa: F401
    InputChannel,
    OutputChannel,
    UserMessage,
    CollectingOutputChannel,
)

# this prevents IDE's from optimizing the imports - we need to import the
# above first, otherwise we will run into import cycles
from bf_nlu_banki.core.channels.socketio import SocketIOInput
from bf_nlu_banki.core.channels.botframework import BotFrameworkInput  # noqa: F401
from bf_nlu_banki.core.channels.callback import CallbackInput  # noqa: F401
from bf_nlu_banki.core.channels.console import CmdlineInput  # noqa: F401
from bf_nlu_banki.core.channels.facebook import FacebookInput  # noqa: F401
from bf_nlu_banki.core.channels.mattermost import MattermostInput  # noqa: F401
from bf_nlu_banki.core.channels.bf_nlu_banki_chat import bf_nlu_bankiChatInput  # noqa: F401
from bf_nlu_banki.core.channels.rest import RestInput  # noqa: F401
from bf_nlu_banki.core.channels.rocketchat import RocketChatInput  # noqa: F401
from bf_nlu_banki.core.channels.slack import SlackInput  # noqa: F401
from bf_nlu_banki.core.channels.telegram import TelegramInput  # noqa: F401
from bf_nlu_banki.core.channels.twilio import TwilioInput  # noqa: F401
from bf_nlu_banki.core.channels.twilio_voice import TwilioVoiceInput  # noqa: F401
from bf_nlu_banki.core.channels.webexteams import WebexTeamsInput  # noqa: F401
from bf_nlu_banki.core.channels.hangouts import HangoutsInput  # noqa: F401

input_channel_classes: List[Type[InputChannel]] = [
    CmdlineInput,
    FacebookInput,
    SlackInput,
    TelegramInput,
    MattermostInput,
    TwilioInput,
    TwilioVoiceInput,
    bf_nlu_bankiChatInput,
    BotFrameworkInput,
    RocketChatInput,
    CallbackInput,
    RestInput,
    SocketIOInput,
    WebexTeamsInput,
    HangoutsInput,
]

# Mapping from an input channel name to its class to allow name based lookup.
BUILTIN_CHANNELS: Dict[Text, Type[InputChannel]] = {
    c.name(): c for c in input_channel_classes
}
