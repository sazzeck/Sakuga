import typing as t

from lightbulb import plugins

if t.TYPE_CHECKING:
    from lightbulb.app import BotApp

plugin = plugins.Plugin(
    "Moderation", description="Moderation commands"
)


# kick

# ban/unban

# time out

# clear or purge channel


def load(bot: "BotApp") -> None:
    bot.add_plugin(plugin)


def unload(bot: "BotApp") -> None:
    bot.remove_plugin(plugin)
