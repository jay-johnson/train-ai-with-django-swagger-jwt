

def convert_to_date(
        value=None,
        format="%Y-%m-%d %H:%M:%S"):
    """convert_to_date

    param: value - datetime object
    param: format - string format
    """

    if value:
        return value.strftime(format)

    return ""
# end of convert_to_date
