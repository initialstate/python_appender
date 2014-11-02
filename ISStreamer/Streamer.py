# local config helper stuff
import configutil
# internet connectivity stuff
import httplib
import json
# time stuff
import datetime
import time
# performance stuff
import threading
import Queue

class Streamer:
    CoreApiBase = ""
    Bucket = ""
    ClientKey = ""
    PubKey = ""
    SubKey = ""
    Channel = ""
    BufferSize = 10
    StreamApiBase = ""
    LogQueue = None
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
            self.ClientKey = config["clientKey"]
        else:
            self.ClientKey = client_key


        self.LogQueue = Queue.Queue(self.BufferSize)
        self.PubKey = config["pkey"]
        self.SubKey = config["skey"]
        self.Channel = config["channel"]
        self.CoreApiBase = config["core_api_base"]
        self.StreamApiBase = config["stream_api_base"]
        self.set_bucket(bucket_name)
        self.Debug = debug

        self.console_message("ClientKey: {clientKey}".format(clientKey=self.ClientKey))
        self.console_message("PubKey: {pubkey}".format(pubkey=self.PubKey))
        self.console_message("SubKey: {subkey}".format(subkey=self.SubKey))
        self.console_message("Channel: {channel}".format(channel=self.Channel))

    

    def set_bucket(self, new_bucket):

        def __create_bucket(new_bucket, client_key):
            conn = httplib.HTTPSConnection(self.CoreApiBase)
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

            if (response.status > 200 and response.status < 300):
                self.console_message("bucket created successfully!")
            else:
                raise Exception("bucket failed: {status} {reason}".format(status=response.status, reason=response.reason))
        self.Bucket = new_bucket
        t = threading.Thread(target=__create_bucket, args=(new_bucket, self.ClientKey))
        t.daemon = False
        t.start()

    def console_message(self, message):
        if (self.Debug):
            print(message)

    def ship_messages(self, messages):
        conn = httplib.HTTPSConnection(self.StreamApiBase)
        resource = "/batch_logs/{ckey}".format(ckey=self.ClientKey)
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'IS PyStreamer Module'
        }
        conn.request('POST', resource, json.dumps(messages), headers)

    def flush(self):
        message = []
        self.console_message("beginning flush")
        while not self.LogQueue.empty():
            messages.append(m)
        self.ship_messages(messages)
        self.console_message("finished flushing queue")


    def log(self, signal, value):
        def __ship_ten():
            i = 10
            messages = []
            while(i > 0):
                m = self.LogQueue.get()
                messages.append(m)

            self.console_message("shipping 10")
            self.ship_messages(messages)
            self.console_message("finished shipping 10")


        def __realtime_log(time_stamp, signal, value):
            if (self.LogQueue.qsize() >= 10):
                t = threading.Thread(target=__ship_ten)
                t.daemon = False
                t.start()
            else:
                log_item = {
                    "bucketId": self.Bucket,
                    "log": value,
                    "date_time": time_stamp,
                    "signal_source": signal
                }
                self.LogQueue.put(log_item)

        timeStamp = time.time()
        gmtime = datetime.datetime.fromtimestamp(timeStamp)
        formatted_gmTime = gmtime.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.console_message("{time}: {signal} {value}".format(signal=signal, value=value, time=formatted_gmTime))

        __reatime_log(signal, value)