"""
File: misc.py 
-------------- 
Miscellaneous utils. 
""" 

import pickle
from datetime import datetime
from pytz import timezone


def timestamp():
    """
    Simple function that retrieves the current date and time
    and returns a properly formatted string (i.e., a timestamp).  
    """
    cal_time = timezone('America/Los_Angeles')
    now = datetime.now(cal_time)
    date_time = now.strftime("%-I-%M-%p-%b-%d-%Y")
    return str(date_time)


def unpickle(filepath):
	"""
	Takes in a path to a pickled 
	.pkl file (type: 'str') and
	returns the unpickled object. 
	"""
	in_file = open(filepath, 'rb')
	loaded_object = pickle.load(in_file) 
	return loaded_object

