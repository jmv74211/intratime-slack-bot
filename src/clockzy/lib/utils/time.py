from datetime import datetime


def get_current_date_time():
    """Get the current date time.

    Returns:
        str: Datetime in format %Y-%m-%d %H:%M:%S
    """

    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    return date_time
