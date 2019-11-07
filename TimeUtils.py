import datetime
from collections import namedtuple
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
    
def days_overlap(datetime_one_start, datetime_one_end, datetime_two_start, datetime_two_end):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=datetime_one_start, end=datetime_one_end)
    r2 = Range(start=datetime_two_start, end=datetime_two_end)
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start).days + 1
    return delta

    