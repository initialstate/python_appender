# ##########################################
# This script is an example
# of how to hit the stream limit
# on a free account, who's cap is set 
# prorated for when then plan is selected.
# ###########################################

from math import ceil
import time, calendar, datetime
from ISStreamer.Streamer import Streamer

now = datetime.datetime.now()
days_in_month = calendar.monthrange(now.year, now.month)[1]
days_left_in_month = float(days_in_month - now.day)
unrounded_prorate = (days_left_in_month / days_in_month)
# roudn the proration up and multiply it by the current free tier allowance
estimated_cap = int((ceil(unrounded_prorate*100) / 100.0) * 25000)

print("Estimated Cap: {}".format(estimated_cap))

stream = Streamer(bucket_name="Testing Cap", bucket_key="cap_testing", buffer_size=100, ini_file_location="./isstreamer.ini", debug_level=2)

for x in range(1, estimated_cap):
	# throttle every 100 events
	if (x%100 == 0):
		time.sleep(1)

	stream.log("event", x)

stream.close()