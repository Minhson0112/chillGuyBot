def formatNumber(number, defaultNumber=0):
    if number is None:
        number = defaultNumber

    return f"{number:,}"
