import asyncio
import logging
import uuid
import os
from functools import partial
from typing import Any, List, Optional, Text, Union, Dict

import bf_nlu_banki.core.utils
from bf_nlu_banki.shared.exceptions import bf_nlu_bankiException
import bf_nlu_banki.shared.utils.common
import bf_nlu_banki.utils
import bf_nlu_banki.utils.common
import bf_nlu_banki.utils.io
from bf_nlu_banki import server, telemetry
from bf_nlu_banki.constants import ENV_SANIC_BACKLOG
from bf_nlu_banki.core import agent, channels, constants
from bf_nlu_banki.core.agent import Agent
from bf_nlu_banki.core.channels import console
from bf_nlu_banki.core.channels.channel import InputChannel
from bf_nlu_banki.core.utils import AvailableEndpoints
import bf_nlu_banki.shared.utils.io
from sanic import Sanic
from asyncio import AbstractEventLoop

logger = logging.getLogger()  # get the root logger


def create_http_input_channels(
    channel: Optional[Text], credentials_file: Optional[Text]
) -> List["InputChannel"]:
    """Instantiate the chosen input channel."""
    if credentials_file:
        all_credentials = bf_nlu_banki.shared.utils.io.read_config_file(credentials_file)
    else:
        all_credentials = {}

    if channel:
        if len(all_credentials) > 1:
            logger.info(
                "Connecting to channel '{}' which was specified by the "
                "'--connector' argument. Any other channels will be ignored. "
                "To connect to all given channels, omit the '--connector' "
                "argument.".format(channel)
            )
        return [_create_single_channel(channel, all_credentials.get(channel))]
    else:
        return [_create_single_channel(c, k) for c, k in all_credentials.items()]


def _create_single_channel(channel: Text, credentials: Dict[Text, Any]) -> Any:
    from bf_nlu_banki.core.channels import BUILTIN_CHANNELS

    if channel in BUILTIN_CHANNELS:
        return BUILTIN_CHANNELS[channel].from_credentials(credentials)
    else:
        # try to load channel based on class name
        try:
            input_channel_class = bf_nlu_banki.shared.utils.common.class_from_module_path(
                channel
            )
            return input_channel_class.from_credentials(credentials)
        except (AttributeError, ImportError):
            raise bf_nlu_bankiException(
                f"Failed to find input channel class for '{channel}'. Unknown "
                f"input channel. Check your credentials configuration to "
                f"make sure the mentioned channel is not misspelled. "
                f"If you are creating your own channel, make sure it "
                f"is a proper name of a class in a module."
            )


def _create_app_without_api(cors: Optional[Union[Text, List[Text]]] = None) -> Sanic:
    app = Sanic("bf_nlu_banki_core_no_api", configure_logging=False)
    server.add_root_route(app)
    server.configure_cors(app, cors)
    return app


def configure_app(
    input_channels: Optional[List["InputChannel"]] = None,
    cors: Optional[Union[Text, List[Text], None]] = None,
    auth_token: Optional[Text] = None,
    enable_api: bool = True,
    response_timeout: int = constants.DEFAULT_RESPONSE_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    route: Optional[Text] = "/webhooks/",
    port: int = constants.DEFAULT_SERVER_PORT,
    endpoints: Optional[AvailableEndpoints] = None,
    log_file: Optional[Text] = None,
    conversation_id: Optional[Text] = uuid.uuid4().hex,
    use_syslog: bool = False,
    syslog_address: Optional[Text] = None,
    syslog_port: Optional[int] = None,
    syslog_protocol: Optional[Text] = None,
    request_timeout: Optional[int] = None,
) -> Sanic:
    """Run the agent."""
    bf_nlu_banki.core.utils.configure_file_logging(
        logger, log_file, use_syslog, syslog_address, syslog_port, syslog_protocol
    )

    if enable_api:
        app = server.create_app(
            cors_origins=cors,
            auth_token=auth_token,
            response_timeout=response_timeout,
            jwt_secret=jwt_secret,
            jwt_method=jwt_method,
            endpoints=endpoints,
        )
    else:
        app = _create_app_without_api(cors)

    if input_channels:
        channels.channel.register(input_channels, app, route=route)
    else:
        input_channels = []

    if logger.isEnabledFor(logging.DEBUG):
        bf_nlu_banki.core.utils.list_routes(app)

    async def configure_async_logging() -> None:
        if logger.isEnabledFor(logging.DEBUG):
            bf_nlu_banki.utils.io.enable_async_loop_debugging(asyncio.get_event_loop())

    app.add_task(configure_async_logging)

    if "cmdline" in {c.name() for c in input_channels}:

        async def run_cmdline_io(running_app: Sanic) -> None:
            """Small wrapper to shut down the server once cmd io is done."""
            await asyncio.sleep(1)  # allow server to start

            await console.record_messages(
                server_url=constants.DEFAULT_SERVER_FORMAT.format("http", port),
                sender_id=conversation_id,
                request_timeout=request_timeout,
            )

            logger.info("Killing Sanic server now.")
            running_app.stop()  # kill the sanic server

        app.add_task(run_cmdline_io)

    return app


def serve_application(
    model_path: Optional[Text] = None,
    channel: Optional[Text] = None,
    interface: Optional[Text] = constants.DEFAULT_SERVER_INTERFACE,
    port: int = constants.DEFAULT_SERVER_PORT,
    credentials: Optional[Text] = None,
    cors: Optional[Union[Text, List[Text]]] = None,
    auth_token: Optional[Text] = None,
    enable_api: bool = True,
    response_timeout: int = constants.DEFAULT_RESPONSE_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    endpoints: Optional[AvailableEndpoints] = None,
    remote_storage: Optional[Text] = None,
    log_file: Optional[Text] = None,
    ssl_certificate: Optional[Text] = None,
    ssl_keyfile: Optional[Text] = None,
    ssl_ca_file: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
    conversation_id: Optional[Text] = uuid.uuid4().hex,
    use_syslog: Optional[bool] = False,
    syslog_address: Optional[Text] = None,
    syslog_port: Optional[int] = None,
    syslog_protocol: Optional[Text] = None,
    request_timeout: Optional[int] = None,
) -> None:
    """Run the API entrypoint."""
    if not channel and not credentials:
        channel = "cmdline"

    input_channels = create_http_input_channels(channel, credentials)

    app = configure_app(
        input_channels,
        cors,
        auth_token,
        enable_api,
        response_timeout,
        jwt_secret,
        jwt_method,
        port=port,
        endpoints=endpoints,
        log_file=log_file,
        conversation_id=conversation_id,
        use_syslog=use_syslog,
        syslog_address=syslog_address,
        syslog_port=syslog_port,
        syslog_protocol=syslog_protocol,
        request_timeout=request_timeout,
    )

    ssl_context = server.create_ssl_context(
        ssl_certificate, ssl_keyfile, ssl_ca_file, ssl_password
    )
    protocol = "https" if ssl_context else "http"

    logger.info(f"Starting bf_nlu_banki server on {protocol}://{interface}:{port}")

    app.register_listener(
        partial(load_agent_on_start, model_path, endpoints, remote_storage),
        "before_server_start",
    )
    app.register_listener(close_resources, "after_server_stop")

    number_of_workers = bf_nlu_banki.core.utils.number_of_sanic_workers(
        endpoints.lock_store if endpoints else None
    )

    telemetry.track_server_start(
        input_channels, endpoints, model_path, number_of_workers, enable_api
    )

    bf_nlu_banki.utils.common.update_sanic_log_level(
        log_file, use_syslog, syslog_address, syslog_port, syslog_protocol
    )

    app.run(
        host=interface,
        port=port,
        ssl=ssl_context,
        backlog=int(os.environ.get(ENV_SANIC_BACKLOG, "100")),
        workers=number_of_workers,
    )


# noinspection PyUnusedLocal
async def load_agent_on_start(
    model_path: Text,
    endpoints: AvailableEndpoints,
    remote_storage: Optional[Text],
    app: Sanic,
    loop: AbstractEventLoop,
) -> Agent:
    """Load an agent.

    Used to be scheduled on server start
    (hence the `app` and `loop` arguments).
    """
    app.ctx.agent = await agent.load_agent(
        model_path=model_path,
        remote_storage=remote_storage,
        endpoints=endpoints,
        loop=loop,
    )
    logger.info("bf_nlu_banki server is up and running.")
    return app.ctx.agent


async def close_resources(app: Sanic, _: AbstractEventLoop) -> None:
    """Gracefully closes resources when shutting down server.

    Args:
        app: The Sanic application.
        _: The current Sanic worker event loop.
    """
    current_agent = getattr(app.ctx, "agent", None)
    if not current_agent:
        logger.debug("No agent found when shutting down server.")
        return

    event_broker = current_agent.tracker_store.event_broker
    if event_broker:
        await event_broker.close()
