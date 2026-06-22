from bot.config.emoji import FARM_GAME_EMOJI


def getItemEmoji(item, default=None):
    if item is None:
        return default

    return FARM_GAME_EMOJI.get(item.icon_image_key, default)


def buildItemText(item, unknownItemText="**item không xác định**"):
    if item is None:
        return unknownItemText

    itemEmoji = getItemEmoji(item)

    if itemEmoji is None:
        return f"**{item.name}**"

    return f"{itemEmoji} **{item.name}**"
