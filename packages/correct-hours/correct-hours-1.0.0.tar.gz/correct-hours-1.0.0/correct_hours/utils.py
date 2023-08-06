import datetime


def parse_date(date_string: str) -> datetime.date:
    parsed_datetime = datetime.datetime.strptime(date_string, "%d/%m/%Y")
    return parsed_datetime.date()