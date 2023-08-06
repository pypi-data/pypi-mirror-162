from datetime import datetime


def create_timestamp(timestamp=None):
    if timestamp:
        ftime = datetime.fromtimestamp(timestamp)
    else:
        ftime = datetime.now()
    return ftime.strftime("%Y-%m-%d %H:%M:%S") 
