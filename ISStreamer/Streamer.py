from Pubnub import Pubnub
from datetime import datetime
import configutil
#import time


class Streamer:
    pub = Pubnub(publish_key="pub-c-92056f77-203d-467a-ba28-c5c8695effb6", subscribe_key="sub-c-1471fc40-4e27-11e4-b332-02ee2ddab7fe", ssl_on=True)
    Bucket = ""
    ClientKey = ""
    def __init__(self, bucket="", clientKey=""):
        config = configutil.getConfig()
        if (config == None or config["bucket"] == None or config["bucket"] == ""):
            self.Bucket = bucket
        else:
            self.Bucket = config["bucket"]
        
        if (config == None or config["key"] == None or config["key"] == ""):
            self.ClientKey = clientKey
        else:
            self.ClientKey = config["key"]


    def realtime_log(self, signal, value, async=True):
        time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        def _callback(r):
            print "{time}: {signal} {value}".format(signal=signal, value=value, time=time)
        def _error(r):
            print "error"

        log = {
            'clientKey': self.ClientKey,
            'bucket': self.Bucket,
            'signal': signal,
            'value': value,
            'time': time
        }
        self.pub.publish(channel='log_streamer', message=log, callback=_callback if async is True else None, error=_error if async is True else None)


    def log(self, signal, value):
        self.realtime_log(signal, value)