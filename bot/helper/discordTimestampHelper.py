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


# Output format:
# - style None: <t:1710000000>
# - style "f": <t:1710000000:f>
def formatTimestamp(value, style: str | None = "f"):
    timestamp = toUnixTimestamp(value)

    if style is None:
        return f"<t:{timestamp}>"

    if style not in VALID_STYLES:
        raise ValueError(f"Invalid Discord timestamp style: {style}")

    return f"<t:{timestamp}:{style}>"


# Output format:
# - <t:1710000000:t>
# - Discord renders this as short local time, for example 16:20
def formatShortTime(value):
    return formatTimestamp(value, "t")


# Output format:
# - <t:1710000000:T>
# - Discord renders this as long local time, for example 16:20:30
def formatLongTime(value):
    return formatTimestamp(value, "T")


# Output format:
# - <t:1710000000:d>
# - Discord renders this as short local date, for example 09/03/2024
def formatShortDate(value):
    return formatTimestamp(value, "d")


# Output format:
# - <t:1710000000:D>
# - Discord renders this as long local date, for example 9 March 2024
def formatLongDate(value):
    return formatTimestamp(value, "D")


# Output format:
# - <t:1710000000:f>
# - Discord renders this as short local date time, for example 9 March 2024 16:20
def formatShortDateTime(value):
    return formatTimestamp(value, "f")


# Output format:
# - <t:1710000000:F>
# - Discord renders this as long local date time, for example Saturday, 9 March 2024 16:20
def formatLongDateTime(value):
    return formatTimestamp(value, "F")


# Output format:
# - <t:1710000000:R>
# - Discord renders this as relative time, for example in 2 hours
def formatRelativeTime(value):
    return formatTimestamp(value, "R")


# Output format:
# - 1710000000
# - Returns an integer Unix timestamp in seconds.
def toUnixTimestamp(value):
    if isinstance(value, datetime):
        return int(normalizeDatetime(value).timestamp())

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    raise TypeError("Discord timestamp value must be datetime, int, or float")


# Output format:
# - timezone-aware datetime
# - Naive datetime values are treated as GMT+7 before timestamp conversion.
def normalizeDatetime(value: datetime):
    if value.tzinfo is None:
        return value.replace(tzinfo=GMT7)

    return value.astimezone(timezone.utc)
