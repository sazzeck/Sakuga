import datetime as dt
import logging
import os
import typing as t

import hikari

from lightbulb import checks, commands, context, decorators, errors, plugins

from sakuga.utils.config import Config

if t.TYPE_CHECKING:
    from lightbulb.app import BotApp

log = logging.getLogger(__name__)

plugin = plugins.Plugin(
    "Owner", default_enabled_guilds=Config.GUILD_ID, description="Owner commands",
)


async def handle_plugins(
    ctx: context.base.Context, plugin_string: str, action: str
) -> None:
    if plugin_string:
        plugins = plugin_string.split(" ")
    else:
        plugins = [e.split(".")[-1] for e in ctx.bot.plugins]

    count = 0
    for plugin in plugins:
        try:
            getattr(ctx.app, f"{action}_extensions")(
                f"sakuga.core.plugins.{plugin.lower()}"
            )
            logging.warning("Plugin '%s' has been %sed.", plugin, action)
            count += 1
        except errors.ExtensionAlreadyLoaded:
            logging.error("Plugin '%s' is already loaded.", plugin)
            await ctx.respond(
                hikari.Embed(
                    title=":gear: Sakuga",
                    description=f"**Plugin `{plugin}` is already loaded :warning:**",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        except errors.ExtensionNotLoaded:
            logging.error("Plugin '%s' is not currently loaded.", plugin)
            await ctx.respond(
                hikari.Embed(
                    title=":gear: Sakuga",
                    description=f"**Plugin `{plugin}` is not currently loaded :warning:**",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await ctx.respond(
                hikari.Embed(
                    title=":gear: Sakuga",
                    description=f"**Plugin `{plugin}` {action}ed :white_check_mark:**",
                    colour=Config.EMBED_COLOR,
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )


choise_plugin = [
    p.strip(".py")
    for p in filter(lambda pl: pl.endswith(".py"), os.listdir("./sakuga/core/plugins"))
]


@plugin.command
@decorators.add_checks(checks.owner_only)
@decorators.command("plugin", "Plugin command group")
@decorators.implements(commands.SlashCommandGroup)
async def cmd_plugin(ctx: context.base.Context) -> None:    # Plugin commands group
    pass


@cmd_plugin.child()
@decorators.option("plugin", "select the plugin", choices=(choise_plugin))
@decorators.command("load", "Load the specified plugin", inherit_checks=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_plugin_load(ctx: context.base.Context) -> None:    # Plugin load command
    await handle_plugins(ctx, ctx.options.plugin, "load")


@cmd_plugin.child()
@decorators.option("plugin", "select the plugin", choices=(choise_plugin))
@decorators.command("reload", "Reload the specified plugin", inherit_checks=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_plugin_reload(ctx: context.base.Context) -> None:    # Plugin reload command
    await handle_plugins(ctx, ctx.options.plugin, "reload")


@cmd_plugin.child()
@decorators.option("plugin", "select the plugin", choices=(choise_plugin))
@decorators.command("unload", "Unload the specified plugin", inherit_checks=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_plugin_unload(ctx: context.base.Context) -> None:    # Plugin unload command
    if ctx.options.plugin == "owner":
        await ctx.respond(
            hikari.Embed(
                title="Sakuga :gear:",
                description="**You cannot unload `owner` plugin :no_entry_sign:**",
                colour=Config.EMBED_COLOR,
                timestamp=dt.datetime.utcnow().astimezone(),
            ),
        )
    else:
        await handle_plugins(ctx, ctx.options.plugin, "unload")


@plugin.command
@decorators.add_checks(checks.owner_only)
@decorators.command("shutdown", "Shut Sakuga down", ephemeral=True)
@decorators.implements(commands.SlashCommand)
async def cmd_shutdown(ctx: context.base.Context) -> None:     # Bot shutdown command
    log.info("Shutdown signal received!")
    await ctx.respond(
        hikari.Embed(
            title="Sakuga :gear:",
            description="**Now shutting down** :wave:",
            colour=Config.EMBED_COLOR,
        ),
    )
    await ctx.app.close()


def load(bot: "BotApp") -> None:
    bot.add_plugin(plugin)


def unload(bot: "BotApp") -> None:
    bot.remove_plugin(plugin)
