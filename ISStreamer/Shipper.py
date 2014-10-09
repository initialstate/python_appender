import httplib
import datetime
import json
import configutil

class Shipper:
    "This is a log streamer written in python that can help stream data directly to Initial State"
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
    
    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def log(self, signal, value, trackerId = ""):
        request_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        conn = httplib.HTTPSConnection("groker-dev.initialstate.com")
        resource = "/logs/{bucket}/{clientKey}".format(bucket=self.Bucket, clientKey=self.ClientKey)
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['User-Agent'] = 'IS PyStreamer Module'

        body = {'log': value, 'date_time': request_time, 'signal_source': signal, 'tracker_id': trackerId}
        print json.dumps(body)
        conn.set_debuglevel(1)
        conn.request("POST", resource, json.dumps(body), headers)



if __name__ == "__main__":
    import sys
    
    config = configutil.getConfig()
    if (len(sys.argv) < 3 and config == None):
        raise Exception("invalid paramteres and no config (or bad config)")

    if (config["key"] == None or config["key"] == ""):
        client_key = sys.argv[2]
    else:
        client_key = config["key"]
    if (config["bucket"] == None or config["bucket"] == ""):
        default_bucket = sys.argv[1]
    else:
        default_bucket = config["bucket"]

    log_streamer = Shipper(default_bucket, client_key)
    log_streamer.log(sys.argv[3], sys.argv[4])