from bot.config.emoji import SERVER_ITEM_EMOJI


def getServerItemEmoji(serverItem, default=None):
    if serverItem is None:
        return default

    return SERVER_ITEM_EMOJI.get(serverItem.icon_image_key, default)


def buildServerItemText(serverItem, unknownItemText="**item không xác định**"):
    if serverItem is None:
        return unknownItemText

    serverItemEmoji = getServerItemEmoji(serverItem)

    if serverItemEmoji is None:
        return f"**{serverItem.name}**"

    return f"{serverItemEmoji} **{serverItem.name}**"
