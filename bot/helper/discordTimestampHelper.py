from datetime import datetime, timedelta, timezone


GMT7 = timezone(timedelta(hours=7))

VALID_STYLES = {
    "t",
    "T",
    "d",
    "D",
    "f",
    "F",
    "R",
}


def formatTimestamp(value, style: str | None = "f"):
    timestamp = toUnixTimestamp(value)

    if style is None:
        return f"<t:{timestamp}>"

    if style not in VALID_STYLES:
        raise ValueError(f"Invalid Discord timestamp style: {style}")

    return f"<t:{timestamp}:{style}>"


def formatShortTime(value):
    return formatTimestamp(value, "t")


def formatLongTime(value):
    return formatTimestamp(value, "T")


def formatShortDate(value):
    return formatTimestamp(value, "d")


def formatLongDate(value):
    return formatTimestamp(value, "D")


def formatShortDateTime(value):
    return formatTimestamp(value, "f")


def formatLongDateTime(value):
    return formatTimestamp(value, "F")


def formatRelativeTime(value):
    return formatTimestamp(value, "R")


def toUnixTimestamp(value):
    if isinstance(value, datetime):
        return int(normalizeDatetime(value).timestamp())

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    raise TypeError("Discord timestamp value must be datetime, int, or float")


def normalizeDatetime(value: datetime):
    if value.tzinfo is None:
        return value.replace(tzinfo=GMT7)

    return value.astimezone(timezone.utc)
