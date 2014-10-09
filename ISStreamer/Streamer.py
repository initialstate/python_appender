from Pubnub import Pubnub
import time
import configutil
import httplib
import json


class Streamer:
    Socket = Pubnub(publish_key="pub-c-92056f77-203d-467a-ba28-c5c8695effb6", subscribe_key="sub-c-1471fc40-4e27-11e4-b332-02ee2ddab7fe", ssl_on=True)
    Bucket = ""
    ClientKey = ""
    def __init__(self, bucket="", clientKey=""):
        config = configutil.getConfig()
        if (config == None and (bucket=="" or clientKey=="")):
            raise Exception("config not found and arguments empty")
        
        if (bucket == ""):
            self.Bucket = config["bucket"]
        else:
            self.Bucket = bucket

        if (clientKey == ""):
            self.ClientKey = config["key"]
        else:
            self.ClientKey = clientKey

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

        self.Socket = Pubnub(publish_key="pub-c-92056f77-203d-467a-ba28-c5c8695effb6", 
            subscribe_key="sub-c-1471fc40-4e27-11e4-b332-02ee2ddab7fe", 
            auth_key=self.ClientKey,
            ssl_on=True)


    def realtime_log(self, signal, value, async=True):
        timeStamp = time.time()
        gmtime = time.gmtime(timeStamp)
        def _callback(r):
            print "{time}: {signal} {value}".format(signal=signal, value=value, time=time.strftime('%Y-%m-%d %H:%M:%S', gmtime))
        def _error(r):
            print "error"

        log = {
            'clientKey': self.ClientKey,
            'bucket': self.Bucket,
            'signal': signal,
            'value': value,
            'time': timeStamp
        }
        self.Socket.publish(channel='log_streamer_local', message=log, callback=_callback if async is True else None, error=_error if async is True else None)


    def log(self, signal, value):
        self.realtime_log(signal, value)