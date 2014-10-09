from Pubnub import Pubnub
import time
import configutil
import httplib
import json
import datetime


class Streamer:
    Socket = None
    Bucket = ""
    ClientKey = ""
    PubKey = ""
    SubKey = ""
    Channel = ""
    def __init__(self, bucket="", clientKey="", apiKeys={}):
        config = configutil.getConfig()
        if (config == None and (bucket=="" or clientKey=="")):
            raise Exception("config not found and arguments empty")
        
        if (bucket == ""):
            self.Bucket = config["bucket"]
        else:
            self.Bucket = bucket

        if (clientKey == ""):
            self.ClientKey = config["clientKey"]
        else:
            self.ClientKey = clientKey

        if ("pkey" in apiKeys):
            self.PubKey = apiKeys["pkey"]
        if ("skey" in apiKeys):
            self.SubKey = apiKeys["skey"]
        if ("channel" in apiKeys):
            self.Channel = apiKeys["channel"]

        if (self.PubKey == "" or self.SubKey == "" or self.Channel == ""):
            self.PubKey = config["pkey"]
            self.SubKey = config["skey"]
            self.Channel = config["channel"]

        print self.PubKey
        print self.SubKey
        print self.Channel
        print self.ClientKey
        conn = httplib.HTTPSConnection("dev-api.initialstate.com")
        resource = "/api/v1/buckets"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'IS PyStreamer Module'
        }
        body = {
            'bucketId': self.Bucket,
            'clientKey': self.ClientKey
        }

        conn.request("POST", resource, json.dumps(body), headers)

        self.Socket = Pubnub(publish_key=self.PubKey, 
            subscribe_key=self.SubKey, 
            auth_key=self.ClientKey,
            ssl_on=True)


    def realtime_log(self, signal, value, async=True):
        timeStamp = time.time()
        gmtime = datetime.datetime.fromtimestamp(timeStamp)
        def _callback(r):
            print "{time}: {signal} {value}".format(signal=signal, value=value, time=gmtime.strftime('%Y-%m-%d %H:%M:%S.%f'))
        def _error(r):
            print "error"

        log = {
            'clientKey': self.ClientKey,
            'bucket': self.Bucket,
            'signal': signal,
            'value': value,
            'time': timeStamp
        }
        self.Socket.publish(channel=self.Channel, message=log, callback=_callback if async is True else None, error=_error if async is True else None)


    def log(self, signal, value):
        self.realtime_log(signal, value)