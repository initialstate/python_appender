import time
from ISStreamer.Streamer import Streamer

logger = Streamer(bucket_name="Stream Example", debug_level=2, offline=True)

logger.log("My Messages", "Stream Starting")
for num in range(1, 100):
        time.sleep(0.1)
        logger.log("My Numbers", num)
        if num%2 == 0:
                logger.log("My Booleans", False)
        else: 
                logger.log("My Booleans", True)
        if num%3 == 0:
                logger.log("My Events", "pop")
        if num%10 == 0:
                logger.log("My Messages", "Stream Half Done")
logger.log("My Messages", "Stream Done")

logger.close()