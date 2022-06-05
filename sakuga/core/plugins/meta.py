import datetime as dt
import time
import typing as t
from platform import python_version

import hikari
from hikari import __version__ as hikari_version

from lightbulb import __version__ as lightbulb_version
from lightbulb import commands, context, decorators, plugins

import psutil
from psutil import Process

from sakuga.utils import Config
from sakuga.utils import chron
from sakuga.utils import const


if t.TYPE_CHECKING:
    from lightbulb.app import BotApp

plugin = plugins.Plugin("Meta", description="Utility commands")


@plugin.command
@decorators.command("about", "View information about Sakuga", ephemeral=True)
@decorators.implements(commands.SlashCommand)
async def cmd_bot_info(ctx: context.base.Context) -> None:    # Bot Information command
    buttons = (
        ctx.app.rest.build_action_row()
        .add_button(hikari.ButtonStyle.LINK, Config.INVITE_URL)
        .set_emoji(ctx.app.cache.get_emoji(978058873388818442))
        .set_label("Invite!")
        .add_to_container()
        .add_button(hikari.ButtonStyle.LINK, Config.GIT_HUB)
        .set_emoji(ctx.app.cache.get_emoji(978059413669699584))
        .set_label("GitHub!")
        .add_to_container()
    )
    with (proc := Process()).oneshot():
        uptime = time.time() - proc.create_time()
        uptime_str = chron.short_delta(dt.timedelta(seconds=uptime))
    mem_of_total = proc.memory_percent()
    await ctx.respond(
        hikari.Embed(
            title=":bookmark_tabs: Bot Information",
            colour=Config.EMBED_COLOR,
        )
        .add_field(
            "Basic packages",
            f"```Python - {python_version()}\nHikari - {hikari_version}\nLightbulb - {lightbulb_version}```",
            inline=False,
        )
        .add_field(
            ":ping_pong: Ping",
            f"`{ctx.app.heartbeat_latency * 1000:,.0f} ms`",
            inline=True,
        )
        .add_field(
            f"{ctx.app.cache.get_emoji(884540996552126524)} RAM",
            f"`{mem_of_total:,.1f}% usage`",
            inline=True,
        )
        .add_field(
            ":busts_in_silhouette: Views",
            f"`{len(ctx.app.cache.get_users_view())} users`",
            inline=True,
        )
        .add_field(
            ":stopwatch: Uptime",
            f"`{uptime_str}`",
            inline=True,
        )
        .add_field(
            f"{ctx.app.cache.get_emoji(927770751367524363)} CPU",
            f"`{psutil.cpu_percent()}% usage`",
            inline=True,
        )
        .add_field(
            f"{ctx.app.cache.get_emoji(884466067920027659)} Currently in",
            f"`{len(ctx.app.cache.get_available_guilds_view())} servers`",
            inline=True,
        ),
        component=buttons
    )


@plugin.command
@decorators.set_help("Group of commands for getting basic information about the server and what is connected with it")
@decorators.command("get_info", "Info command group", ephemeral=True)
@decorators.implements(commands.SlashCommandGroup)
async def get_info_group(ctx: context.base.Context) -> None:    # Group of commands to get information
    pass


@get_info_group.child
@decorators.command("guild", "Get information about the guild", ephemeral=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_guild_info(ctx: context.base.Context) -> None:    # Guild Information command
    assert ctx.guild_id is not None
    guild = ctx.app.cache.get_available_guild(ctx.guild_id)
    assert guild is not None

    invites = len(await guild.app.rest.fetch_guild_invites(ctx.guild_id))
    roles = len(await guild.app.rest.fetch_roles(ctx.guild_id))
    bans = len(await guild.app.rest.fetch_bans(ctx.guild_id))
    members = guild.get_members()
    channels = guild.get_channels()
    presences = guild.get_presences()
    level = guild.premium_tier.value
    boost = guild.premium_subscription_count

    online = 0
    idle = 0
    dnd = 0

    for p in presences.values():
        if p.visible_status == hikari.Status.ONLINE:
            online += 1
        elif p.visible_status == hikari.Status.IDLE:
            idle += 1
        elif p.visible_status == hikari.Status.DO_NOT_DISTURB:
            dnd += 1

    voice = 0
    text = 0
    nsfw = 0

    for c in channels.values():
        if c.is_nsfw:
            nsfw += 1
        elif c.type == hikari.ChannelType.GUILD_VOICE:
            voice += 1
        elif c.type == hikari.ChannelType.GUILD_TEXT:
            text += 1

    human = 0
    bots = 0

    for m in members.values():
        if not m.is_bot:
            human += 1
        if m.is_bot:
            bots += 1

    await ctx.respond(
        hikari.Embed(
            title=f":busts_in_silhouette: {guild.name}",
            description="\n".join(
                [
                    f"• **ID:** {guild.id}",
                    f"• **Owner:** <@{guild.owner_id}> `id: {guild.owner_id}`",
                    f"• **Nitro level:** {level} `boost: {boost}`",
                    f"• **Preferred locale:** {guild.preferred_locale.name}",
                    f"""```
Community - {"✓" if "COMMUNITY" in guild.features else "✗"}
Partner - {"✓" if "PARTNERED" in guild.features else "✗"}
Verified - {"✓" if "VERIFIED" in guild.features else "✗"}
Discoverable - {"✓" if "DISCOVERABLE" in guild.features else "✗"}
Monetization - {"✓" if "MONETIZATION_ENABLED" in guild.features else "✗"}
```""",
                ],
            ),
            colour=Config.EMBED_COLOR,
        )
        .add_field(
            "Guild",
            f">>> Invites: {invites}\nRoles: {roles}\nBans: {bans}",
            inline=True,
        )
        .add_field(
            "Channels",
            f">>> Voice: {voice}\nText: {text}\nNSFW: {nsfw}",
            inline=True,
        )
        .add_field(
            "Members",
            f">>> Total: {len(members)}\nHumans: {human}\nBots: {bots}",
            inline=True,
        )
        .set_image(guild.banner_url)
        .add_field(
            "Created at",
            f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True,
        )
        .add_field(
            "Statuses",
            " ".join(
                [
                    f"🟢 {online}",
                    f"🟠 {idle}",
                    f"🔴 {dnd}",
                    f"⚪ {len(members) - (online + idle + dnd)}",
                ],
            ),
            inline=True,
        )
        .set_thumbnail(guild.icon_url),
    )


@get_info_group.child
@decorators.option("role", "select a role", hikari.Role)
@decorators.command("role", "Get information about the role", ephemeral=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_role_info(ctx: context.base.Context) -> None:    # Role Information command
    assert ctx.guild_id and ctx.options.role is not None
    guild = ctx.app.cache.get_available_guild(ctx.guild_id)
    assert guild is not None

    role = ctx.options.role
    members = guild.get_members()

    await ctx.respond(
        hikari.Embed(
            title=":label: Role information",
            description="\n".join(
                [
                    f"• **Name:** `{role.name}`",
                    f"• **ID:** {role.id}",
                    f"• **Members:** `{len([m for m in  members.values() if role.id in m.role_ids])}`",
                    f"• **Position:** `{role.position}`",
                    f"""```Administrator - {'✓' if bool(role.permissions & hikari.Permissions.ADMINISTRATOR) else '✗'}
Mentionable - {'✓' if role.is_mentionable else '✗'}
Managed - {'✓' if role.is_managed else '✗'}
Premium - {'✓' if role.is_premium_subscriber_role else '✗'}```""",
                ],
            ),
            colour=Config.EMBED_COLOR,
        ).add_field(
            "Created at",
            f"<t:{int(role.created_at.timestamp())}:R>",
            inline=False,
        ),
    )


@get_info_group.child
@decorators.option("target", "select a user", hikari.User)
@decorators.command("user", "Get information about the user", ephemeral=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_user_info(ctx: context.base.Context) -> None:    # User Information command
    assert ctx.guild_id and ctx.options.target is not None
    member = ctx.app.cache.get_member(ctx.guild_id, ctx.options.target)
    assert member is not None

    badge_emoji_mapping = {
        hikari.UserFlag.BUG_HUNTER_LEVEL_1: const.EMOJI_BUGHUNTER,
        hikari.UserFlag.BUG_HUNTER_LEVEL_2: const.EMOJI_BUGHUNTER_GOLD,
        hikari.UserFlag.DISCORD_CERTIFIED_MODERATOR: const.EMOJI_CERT_MOD,
        hikari.UserFlag.EARLY_SUPPORTER: const.EMOJI_EARLY_SUPPORTER,
        hikari.UserFlag.EARLY_VERIFIED_DEVELOPER: const.EMOJI_VERIFIED_DEVELOPER,
        hikari.UserFlag.HYPESQUAD_EVENTS: const.EMOJI_HYPESQUAD_EVENTS,
        hikari.UserFlag.HYPESQUAD_BALANCE: const.EMOJI_HYPESQUAD_BALANCE,
        hikari.UserFlag.HYPESQUAD_BRAVERY: const.EMOJI_HYPESQUAD_BRAVERY,
        hikari.UserFlag.HYPESQUAD_BRILLIANCE: const.EMOJI_HYPESQUAD_BRILLIANCE,
        hikari.UserFlag.PARTNERED_SERVER_OWNER: const.EMOJI_PARTNER,
        hikari.UserFlag.DISCORD_EMPLOYEE: const.EMOJI_STAFF,
    }

    badges = [
        emoji for flag, emoji in badge_emoji_mapping.items() if flag & member.flags
    ]
    roles = [
        role.mention
        for role in sorted(member.get_roles(), key=lambda r: r.position, reverse=True)
    ]
    roles.remove(f"<@&{ctx.guild_id}>")

    show_roles = "**,** ".join(roles) if roles else "`✗`"
    show_badges = " ".join(badges or "`✗`")
    cdu = member.communication_disabled_until()

    await ctx.respond(
        hikari.Embed(
            title=":bust_in_silhouette: User information",
            description="\n".join(
                [
                    f"• **Username:** `{member}`",
                    f"• **Nickname:** `{member.nickname or '✗'}`",
                    f"• **ID:** {member.id}",
                    f"• **Bot:** `{'✓' if member.is_bot else '✗'}`",
                ],
            ),
            colour=Config.EMBED_COLOR,
        )
        .add_field(
            "Created at",
            f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )
        .add_field(
            "Joined at",
            f"<t:{int(member.joined_at.timestamp())}:R>",
            inline=True,
        )
        .add_field(
            "Timed out",
            f"<t:{int(cdu.timestamp())}:R>" if cdu is not None else "`✗`",
            inline=True,
        )
        .add_field(
            f"Roles: {len(roles)}",
            f">>> {show_roles}",
            inline=False,
        )
        .add_field(
            f"Badges: {len(badges)}",
            f"> {show_badges}",
            inline=False,
        )
        .set_thumbnail(ctx.options.target.display_avatar_url),
    )


def channel_type(channel: hikari.GuildChannel) -> str:
    if channel.type == hikari.ChannelType.GUILD_CATEGORY:
        str_channel_type = "category"
    elif channel.type == hikari.ChannelType.GUILD_TEXT:
        str_channel_type = "text"
    elif channel.type == hikari.ChannelType.GUILD_VOICE:
        str_channel_type = "voice"
    elif channel.type == hikari.ChannelType.GUILD_NEWS:
        str_channel_type = "news"
    elif channel.type == hikari.ChannelType.GUILD_STAGE:
        str_channel_type = "stage"

    return str_channel_type


@get_info_group.child
@decorators.option("channel", "select a channel", hikari.GuildChannel)
@decorators.command("channel", "Get information about the channel", ephemeral=True)
@decorators.implements(commands.SlashSubCommand)
async def cmd_channel_info(ctx: context.base.Context) -> None:    # Channel Information command
    assert ctx.guild_id and ctx.options.channel is not None
    guild = ctx.app.cache.get_available_guild(ctx.guild_id)
    assert guild is not None

    channel = guild.get_channel(ctx.options.channel.id)

    if isinstance(channel, hikari.GuildCategory):
        ...
    elif isinstance(channel, hikari.GuildNewsChannel):
        ...
    elif isinstance(channel, hikari.GuildStageChannel):
        ...
    elif isinstance(channel, hikari.GuildVoiceChannel):
        ...
    elif isinstance(channel, hikari.GuildTextChannel):
        ...

    await ctx.respond()


@plugin.command
@decorators.option("target", "select a user", hikari.User)
@decorators.command("avatar", "Get user avatar", ephemeral=True)
@decorators.implements(commands.SlashCommand)
async def cmd_user_avatar(ctx: context.base.Context) -> None:    # View avatar user command
    assert ctx.guild_id and ctx.options.target is not None
    member = ctx.app.cache.get_member(ctx.guild_id, ctx.options.target)
    assert member is not None

    await ctx.respond(
        hikari.Embed(
            colour=Config.EMBED_COLOR,
        )
        .set_footer(f"• {member.display_name}'s avatar")
        .set_image(member.avatar_url or member.default_avatar_url),
    )


def load(bot: "BotApp") -> None:
    bot.add_plugin(plugin)


def unload(bot: "BotApp") -> None:
    bot.remove_plugin(plugin)
