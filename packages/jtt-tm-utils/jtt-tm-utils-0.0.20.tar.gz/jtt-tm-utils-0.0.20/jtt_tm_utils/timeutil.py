from datetime import datetime
def linux_timestamp():
    return int(datetime.now().timestamp())

def timestamp_ms():
    return datetime.now().timestamp()*1000

def time_to_microsec_str(d=None):
    if d is None:
        d = datetime.now()
    return d.strftime('%Y%m%d%H%M%S%f')

def time_to_sql_str(d=None):
    if d is None:
        d = datetime.now()

    return d.strftime('%Y-%m-%d %H:%M:%S')

def date_to_sql_str(d=None):
    if d is None:
        d = datetime.now()

    return d.strftime('%Y-%m-%d')