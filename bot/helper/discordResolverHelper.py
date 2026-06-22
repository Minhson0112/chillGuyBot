import discord


async def resolveChannel(bot, channelId: int, channelType=None):
    channel = bot.get_channel(channelId)

    if channel is None:
        try:
            channel = await bot.fetch_channel(channelId)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None

    if channelType is not None and not isinstance(channel, channelType):
        return None

    return channel


async def resolveGuildMember(guild: discord.Guild, userId: int):
    member = guild.get_member(userId)

    if member is not None:
        return member

    try:
        return await guild.fetch_member(userId)
    except (discord.NotFound, discord.HTTPException):
        return None


async def resolveMemberDisplayName(bot, guild, userId: int):
    if guild is not None:
        guildMember = guild.get_member(userId)

        if guildMember is not None:
            return guildMember.display_name

    user = bot.get_user(userId)

    if user is None:
        try:
            user = await bot.fetch_user(userId)
        except Exception:
            user = None

    if user is not None:
        return user.display_name

    return str(userId)
