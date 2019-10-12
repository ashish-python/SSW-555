import datetime
#receive two datetime objects, and return the difference in days
#datetime_one should be an earlier date than datetime_two or it will return False

def datetime_delta(datetime_one, datetime_two):
    return datetime_two - datetime_one

def legitimate_date(date_str):
    try:
        date = datetime.datetime.strptime(date_str, "%d %b %Y")
    except:
        return False
    return date

def datetime_to_string(dt):
    try:
        return datetime.datetime.strftime(dt, "%d %b %Y")
    except:
        return False

    