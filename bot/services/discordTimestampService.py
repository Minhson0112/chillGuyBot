from datetime import datetime, timedelta, timezone


class DiscordTimestampService:
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

    def formatTimestamp(self, value, style: str | None = "f"):
        timestamp = self.toUnixTimestamp(value)

        if style is None:
            return f"<t:{timestamp}>"

        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid Discord timestamp style: {style}")

        return f"<t:{timestamp}:{style}>"

    def formatShortTime(self, value):
        return self.formatTimestamp(value, "t")

    def formatLongTime(self, value):
        return self.formatTimestamp(value, "T")

    def formatShortDate(self, value):
        return self.formatTimestamp(value, "d")

    def formatLongDate(self, value):
        return self.formatTimestamp(value, "D")

    def formatShortDateTime(self, value):
        return self.formatTimestamp(value, "f")

    def formatLongDateTime(self, value):
        return self.formatTimestamp(value, "F")

    def formatRelativeTime(self, value):
        return self.formatTimestamp(value, "R")

    def toUnixTimestamp(self, value):
        if isinstance(value, datetime):
            return int(self.normalizeDatetime(value).timestamp())

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        raise TypeError("Discord timestamp value must be datetime, int, or float")

    def normalizeDatetime(self, value: datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=self.GMT7)

        return value.astimezone(timezone.utc)


discordTimestampService = DiscordTimestampService()
