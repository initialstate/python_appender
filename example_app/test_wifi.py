import time
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="Testing Wifi", ini_file_location="./isstreamer.ini")

try:
        for num in range(1, 1000):
                streamer.log("num", num)
                print("iteration #{}".format(num))
                time.sleep(1)
                streamer.flush()
except Exception as ex:
        print(ex)

streamer.close()