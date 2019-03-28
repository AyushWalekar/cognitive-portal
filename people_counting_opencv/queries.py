from datetime import datetime, timedelta
from app.ApplicationContext import ApplicationContext

app_context = ApplicationContext.getApplicationContext()
app_props = app_context.get_props()


def get_iso_date(Y, m, d, h=None, M=None, S=None):
    """
    Generic function to convert date tuple into iso format
    :param Y: year
    :param m: month
    :param d: date
    :param h: hour
    :param M: minute
    :param S: second
    :return: date in ISO format
    """
    if S is None:
        if M is None:
            if h is None:
                return datetime(Y, m, d).isoformat()
            return datetime(Y, m, d, h).isoformat()
        return datetime(Y, m, d, h, M).isoformat()
    return datetime(Y, m, d, h, M, S).isoformat()


def get_logs(from_time: datetime, to_time: datetime = None):
    """

    :rtype: list of json obj
    """
    # iso_time_format_str = "%Y-%m-%dT%H:%M:%SZ"
    # from_time = datetime.strptime(from_date_str, iso_time_format_str)
    # to_time = datetime.strptime(to_date_str, iso_time_format_str)
    if to_time is None:
        to_time = datetime.now()
    db_connector = app_context.db_connector
    # db = db_connector.db
    collection = db_connector.collection
    print("Getting logs.. ", " From: ", from_time, " To: ", to_time)
    result_set = collection.find({"date": {"$gt": from_time, "$lt": to_time}})
    return list(result_set)


def get_logs_from_date_str(from_time: str, to_time: str = None):
    if to_time is None:
        return get_logs(get_date_from_str(from_time))
    return get_logs(get_date_from_str(from_time), get_date_from_str(to_time))


def get_date_from_str(date_str):
    # date_time_format_str = "%Y-%m-%dT%H:%M:%SZ"
    date_time_format_str = app_props["query"]["date_time_format_str"]
    print("Date time format is: ", date_time_format_str)
    return datetime.strptime(date_str, date_time_format_str)


def get_todays_logs():
    curr_time = datetime.now()
    from_time = curr_time.replace(hour=0, minute=0, second=0)
    return get_logs(from_time, curr_time)


def get_that_days_logs(date):
    from_time = date.replace(hour=0, minute=0, second=0)
    to_time = date.replace(hour=23, minute=59, second=59)
    return get_logs(from_time, to_time)


def get_past_logs(days=0, hours=0, minutes=0, weeks=0, months=0, years=0):
    if years != 0:
        weeks += years * 52
    if months != 0:
        weeks += months * 4

    curr_time = datetime.now()
    from_time = curr_time - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)

    if hours == 0 or minutes == 0:
        from_time = from_time.replace(hour=0, minute=0)
    return get_logs(from_time, curr_time)


# result = get_todays_logs()
# result = get_past_logs(months=1)
result = get_logs_from_date_str("2019-01-01T01:01:01Z")
# result = get_that_days_logs(datetime(2019, 3, 12))
print(list(result).__len__())
