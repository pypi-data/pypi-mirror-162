from datetime import datetime


def n() -> datetime:
    return datetime.now()


def get_date_string() -> str:
    return n().strftime("%Y-%m-%d")


def get_time_string() -> str:
    return n().strftime("%H%M")


def get_day_of_year():
    return int(datetime.now().timetuple().tm_yday)
