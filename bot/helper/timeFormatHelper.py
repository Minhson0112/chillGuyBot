def formatMinutesSeconds(totalSeconds: int, padMinutes: bool = False):
    minutes = totalSeconds // 60
    seconds = totalSeconds % 60
    minuteText = f"{minutes:02d}" if padMinutes else str(minutes)

    return f"{minuteText}:{seconds:02d}"


def formatCompactDuration(totalSeconds: int):
    minutes = totalSeconds // 60
    seconds = totalSeconds % 60

    if minutes <= 0:
        return f"{seconds}s"

    if seconds <= 0:
        return f"{minutes}m"

    return f"{minutes}m{seconds:02d}s"


def formatHoursMinutesSeconds(totalSeconds: int):
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = totalSeconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def formatMillisecondsMinutesSeconds(value, emptyText: str = "--:--"):
    if value is None:
        return emptyText

    totalSeconds = int(value) // 1000

    return formatMinutesSeconds(totalSeconds, padMinutes=True)
