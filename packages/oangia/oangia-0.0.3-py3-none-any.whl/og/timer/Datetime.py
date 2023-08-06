import time
from datetime import datetime

class Datetime:
	def datetimeToTimestamp(datetime_str):
    		obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    		timestamp = datetime.timestamp(obj)
    		return int(timestamp)

	def timestampToDatetime(timestamp):
    		dt_object = datetime.fromtimestamp(timestamp)
    		return dt_object.strftime('%Y-%m-%d %H:%M:%S')