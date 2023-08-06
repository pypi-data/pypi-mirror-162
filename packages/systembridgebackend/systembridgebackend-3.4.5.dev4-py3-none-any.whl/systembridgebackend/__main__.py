"""System Bridge: Main"""
import asyncio
import logging
import sys

from hypercorn.asyncio import serve
from hypercorn.config import Config
from systembridgeshared.const import (
    SETTING_AUTOSTART,
    SETTING_LOG_LEVEL,
    SETTING_PORT_API,
)
from systembridgeshared.database import Database
from systembridgeshared.logger import setup_logger
from systembridgeshared.settings import Settings

from .autostart import autostart_disable, autostart_enable
from .modules.system import System
from .server import app
from .shortcut import create_shortcuts

if __name__ == "__main__":

    database = Database()
    settings = Settings(database)

    LOG_LEVEL = str(settings.get(SETTING_LOG_LEVEL))
    setup_logger(LOG_LEVEL, "system-bridge")

    logger = logging.getLogger(__name__)

    if "--init" in sys.argv:
        logger.info("Initialized application. Exiting now.")
        sys.exit(0)

    logger.info("System Bridge %s: Startup", System().version())

    if "--cli" not in sys.argv:
        autostart = settings.get(SETTING_AUTOSTART)
        logger.info("Autostart enabled: %s", autostart)
        if autostart:
            autostart_enable()
        else:
            autostart_disable()

        create_shortcuts()

    if (port := settings.get(SETTING_PORT_API)) is None:
        raise ValueError("Port not set")
    log_level = settings.get(SETTING_LOG_LEVEL)
    logger.info("Configuring server for port: %s", port)

    config = Config()
    config.bind = [f"localhost:{port}"]
    if log_level is not None:
        config.loglevel = str(log_level)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        serve(
            app,  # type: ignore
            config,
            shutdown_trigger=lambda: asyncio.Future(),  # pylint: disable=lambda-may-not-be-necessary
        ),
    )

    logger.info("Server stopped")
