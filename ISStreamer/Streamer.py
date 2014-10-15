# local config helper stuff
import configutil
# internet connectivity stuff
from Pubnub import Pubnub
import httplib
import json
# time stuff
import datetime
import time
# performance stuff
import threading


class Streamer:
    Socket = None
    Bucket = ""
    ClientKey = ""
    PubKey = ""
    SubKey = ""
    Channel = ""
    Debug = False
    def __init__(self, bucket="", client_key="", ini_file_location=None, debug=False):

        config = configutil.getConfig(ini_file_location)

        if (config == None and bucket=="" and client_key == ""):
            raise Exception("config not found and arguments empty")
        
        if (bucket == ""):
            bucket_name = config["bucket"]
        else:
            bucket_name = bucket
        if (client_key == ""):
            self.ClientKey = client_key
        else:
            self.ClientKey = config["clientKey"]

        self.PubKey = config["pkey"]
        self.SubKey = config["skey"]
        self.Channel = config["channel"]
        self.set_bucket(bucket_name)
        self.Debug = debug

        self.console_message("ClientKey: {clientKey}".format(clientKey=self.ClientKey))
        self.console_message("PubKey: {pubkey}".format(pubkey=self.PubKey))
        self.console_message("SubKey: {subkey}".format(subkey=self.SubKey))
        self.console_message("Channel: {channel}".format(channel=self.Channel))
        
        self.Socket = Pubnub(publish_key=self.PubKey, 
            subscribe_key=self.SubKey, 
            auth_key=self.ClientKey,
            ssl_on=True)

    

    def set_bucket(self, new_bucket):

        def __create_bucket(new_bucket, client_key):
            conn = httplib.HTTPSConnection("dev-api.initialstate.com")
            resource = "/api/v1/buckets"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'IS PyStreamer Module'
            }
            body = {
                'bucketId': new_bucket,
                'clientKey': client_key
            }

            conn.request("POST", resource, json.dumps(body), headers)

            response = conn.getresponse()
            time.sleep(3)

            if (response.status > 200 and response.status < 300):
                pass
            else:
                raise Exception("bucket failed: {status} {reason}".format(status=response.status, reason=response.reason))
        self.Bucket = new_bucket
        t = threading.Thread(target=__create_bucket, args=(new_bucket, self.ClientKey))
        t.daemon = True
        t.start()

    def console_message(self, message):
        if (self.Debug):
            print(message)

    def realtime_log(self, signal, value, async=True):
        timeStamp = time.time()
        gmtime = datetime.datetime.fromtimestamp(timeStamp)
        self.console_message("{time}: {signal} {value}".format(signal=signal, value=value, time=gmtime.strftime('%Y-%m-%d %H:%M:%S.%f')))
        def _callback(r):
            pass
        def _error(r):
            self.console_message("error sending message: {r}".format(r=r))

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