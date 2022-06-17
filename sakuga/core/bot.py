import logging

from aiohttp import ClientSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import hikari
from hikari import events

import lightbulb

from sakuga.utils import Config
from sakuga.utils.const import CACHE


class Bot(lightbulb.BotApp):
    def __init__(self) -> None:
        self.log = logging.getLogger("sakuga")
        self.scheduler = AsyncIOScheduler()
        self.session = ClientSession()

        super().__init__(
            token=Config.TOKEN,
            owner_ids=Config.OWNER_IDS,
            help_slash_command=True,
            intents=hikari.Intents.ALL,
            cache_settings=CACHE,
        )

        subscriptions = {
            events.StartingEvent: self.on_starting,
            events.StartedEvent: self.on_started,
            events.StoppingEvent: self.on_stopping,
            lightbulb.CommandErrorEvent: self.on_error,
        }
        for e, c in subscriptions.items():
            self.event_manager.subscribe(e, c)

    async def on_starting(self, _: events.StartingEvent) -> None:
        self.load_extensions_from("./sakuga/core/plugins")
        self.scheduler.start()
        self.session

    async def on_started(self, _: events.StartedEvent) -> None:
        ping = self.heartbeat_latency * 1000
        if ping >= 300:
            self.log.critical(f"Ping: {ping:,.0f} ms")
        elif 150 <= ping < 300:
            self.log.warning(f"Ping: {ping:,.0f} ms")
        else:
            self.log.info(f"Ping: {ping:,.0f} ms")

    async def on_stopping(self, _: events.StoppingEvent) -> None:
        self.scheduler.shutdown()
        await self.session.close()

        self.log.warning("Bot shutdown.")

    async def on_error(self, event: lightbulb.CommandErrorEvent) -> None:
        exception = event.exception.__cause__ or event.exception
        if isinstance(exception, lightbulb.NotOwner):
            await event.context.respond(
                hikari.Embed(
                    title=":interrobang: Error handler",
                    description="**You are not the owner of this bot**",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        elif isinstance(exception, lightbulb.BotMissingRequiredPermission):
            await event.context.respond(
                hikari.Embed(
                    title=":interrobang: Error handler",
                    description=f"""**The bot doesn't have enough rights to execute this command:**
 `{event.context.command.qualname}`""",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        elif isinstance(exception, lightbulb.MissingRequiredPermission):
            await event.context.respond(
                hikari.Embed(
                    title=":interrobang: Error handler",
                    description=f"""**You don't have permission to use this command:
 `{event.context.command.qualname}`**""",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        elif isinstance(exception, lightbulb.NSFWChannelOnly):
            await event.context.respond(
                hikari.Embed(
                    title=":interrobang: Error handler",
                    description=f"""**The command `{event.context.command.qualname}`
 can only be used inside a NSFW channel** :underage:""",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await event.context.respond(
                hikari.Embed(
                    title=":interrobang: Error handler",
                    description="**An unknown error has occurred**",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            raise exception
