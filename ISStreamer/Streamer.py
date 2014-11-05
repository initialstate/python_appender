# local config helper stuff
try:
    import ISStreamer.configutil as configutil
except ImportError:
    import configutil
try:
    import ISStreamer.version as version
except ImportError:
    import version
import uuid

# python 2 and 3 conversion support
import sys
if (sys.version_info < (2,7,0)):
    sys.stderr.write("You need at least python 2.7.0 to use the ISStreamer")
    exit(1)
elif (sys.version_info >= (3,0)):
    import http.client as httplib
    import queue as Queue
else:
    import httplib
    import Queue
import json
# time stuff
import datetime
import time
# performance stuff
import threading

class Streamer:
    CoreApiBase = ""
    Bucket = ""
    ClientKey = ""
    PubKey = ""
    SubKey = ""
    Channel = ""
    BufferSize = 20
    StreamApiBase = ""
    LogQueue = None
    DebugLevel = 0
    SessionId = ""
    IsClosed = True
    def __init__(self, bucket="", client_key="", ini_file_location=None, debug_level=0):
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
        self.CoreApiBase = config["core_api_base"]
        self.StreamApiBase = config["stream_api_base"]
        self.set_bucket(bucket_name)
        self.DebugLevel = debug_level
        self.IsClosed = False

        self.console_message("ClientKey: {clientKey}".format(clientKey=self.ClientKey))
        self.console_message("core_api_base: {api}".format(api=self.CoreApiBase))
        self.console_message("stream_api_base: {api}".format(api=self.StreamApiBase))
    

    def set_bucket(self, new_bucket, retries=3):

        def __create_bucket(new_bucket, bucket_id, client_key):
            api_base = self.CoreApiBase
            conn = None
            if (self.CoreApiBase.startswith('https://')):
                api_base = self.CoreApiBase[8:]
                self.console_message("core api base domain: {domain}".format(domain=api_base), level=2)
                conn = httplib.HTTPSConnection(api_base)
            else:
                api_base = self.CoreApiBase[7:]
                self.console_message("core api base domain: {domain}".format(domain=api_base), level=2)
                conn = httplib.HTTPConnection(api_base)
            resource = "/api/v1/buckets"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'PyStreamer v' + version.__version__
            }
            body = {
                'bucketId': bucket_id,
                'bucketName': new_bucket,
                'clientKey': client_key
            }

            def ___ship(retry_attempts, wait=0):
                if (retry_attempts <= 0):
                    if (self.DebugLevel >= 2):
                        raise Exception("bucket create failed")
                    else:
                        self.console_message("ISStreamer failed to create or find bucket after a number of attempts", level=0)
                        return

                try:
                    if (wait > 0):
                        time.sleep(wait)
                    conn.request("POST", resource, json.dumps(body), headers)
                    response = conn.getresponse()

                    if (response.status >= 200 and response.status < 300):
                        self.console_message("bucket created successfully!", level=2)
                    else:
                        self.console_message("ISStreamer failed to setup the bucket on attempt {atmpt}. StatusCode: {sc}; Reason: {r}".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
                        raise Exception("ship exception")
                except:
                    self.console_message("exception creating bucket on attempt {atmpt}.".format(atmpt=retry_attempts))
                    retry_attempts = retry_attempts - 1
                    ___ship(retry_attempts, 1)

            ___ship(retries)

        self.SessionId = str(uuid.uuid4())
        self.Bucket = new_bucket
        t = threading.Thread(target=__create_bucket, args=(new_bucket, self.SessionId, self.ClientKey))
        t.daemon = False
        t.start()

    def console_message(self, message, level=1):
        if (self.DebugLevel >= level):
            print(message)

    def ship_messages(self, messages, retries=3):
        api_base = self.StreamApiBase
        conn = None
        if (self.StreamApiBase.startswith('https://')):
            api_base = self.StreamApiBase[8:]
            self.console_message("stream api base domain: {domain}".format(domain=api_base), level=2)
            conn = httplib.HTTPSConnection(api_base)
        else:
            api_base = self.StreamApiBase[7:]
            self.console_message("stream api base domain: {domain}".format(domain=api_base), level=2)
            conn = httplib.HTTPConnection(api_base)
        resource = "/batch_logs"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PyStreamer v' + version.__version__,
            'X-IS-ClientKey': self.ClientKey
        }

        self.console_message("ship it!", level=2)

        def __ship(retry_attempts, wait=0):
            if (retry_attempts <= 0):
                if (self.DebugLevel >= 2):
                    raise Exception("shipping logs failed.. network issue?")
                else:
                    self.console_message("ISStreamer failed to ship the logs after a number of attempts {msgs}".format(msgs=json.dumps(messages)), level=0)
                    return
            
            try:
                if (wait > 0):
                    time.sleep(wait)
                conn.request('POST', resource, json.dumps(messages), headers)
                response = conn.getresponse()

                if (response.status >= 200 and response.status < 300):
                    self.console_message("ship success!", level=2)
                else:
                    self.console_message("ship failed on attempt {atmpt} (StatusCode: {sc}; Reason: {r})".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
                    raise Exception("ship exception")
            except:
                self.console_message("exception shipping logs on attempt {atmpt}.".format(atmpt=retry_attempts))
                retry_attempts = retry_attempts - 1
                __ship(retry_attempts, 1)

        __ship(retries)
            

    def flush(self):
        messages = []
        self.console_message("checking queue", level=2)
        while not self.LogQueue.empty():
            m = self.LogQueue.get()
            messages.append(m)
        if len(messages) > 0:
            self.console_message("queue not empty, flushing", level=2)
            self.ship_messages(messages)
        self.console_message("finished flushing queue", level=2)


    def log(self, signal, value):
        def __ship_ten():
            i = 10
            messages = []
            while(i > 0):
                m = self.LogQueue.get()
                messages.append(m)
                i = i - 1

            self.console_message("shipping 10", level=2)
            self.ship_messages(messages)
            self.console_message("finished shipping 10", level=2)


        timeStamp = time.time()
        gmtime = datetime.datetime.fromtimestamp(timeStamp)
        formatted_gmTime = gmtime.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.console_message("{time}: {signal} {value}".format(signal=signal, value=value, time=formatted_gmTime))
        if (self.LogQueue.qsize() >= 10):
            self.console_message("queue size greater than 10, shipping!")
            t = threading.Thread(target=__ship_ten)
            t.daemon = False
            t.start()
    
        self.console_message("queueing log item")
        log_item = {
            "bucketId": self.Bucket,
            "log": value,
            "date_time": formatted_gmTime,
            "signal_source": signal,
            "epoc": timeStamp,
            "tracker_id": self.SessionId
        }
        self.LogQueue.put(log_item)

    def close(self):
        self.IsClosed = True
        self.flush()

    def __del__(self):
        """Try to close/flush the cache before destruction"""
        try:
            if (not self.IsClosed):
                self.flush()
        except:
            if (self.DebugLevel >= 2):
                raise Exception("failed to close the buffer, make sure to explicitly call close() on the Streamer")
            else:
                self.console_message("failed to close the buffer, make sure to explicitly call close() on the Streamer", level=1)
