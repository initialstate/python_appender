import httplib
import datetime
import json

class Streamer:
    "This is a log streamer written in python that can help stream data directly to Initial State"
    Bucket = ""
    ClientKey = ""
    def __init__(self, bucket="", clientKey=""):
        config = getConfig()
        if (config == None or config["bucket"] == None or config["bucket"] == ""):
            self.Bucket = bucket
        else:
            self.Bucket = config["bucket"]
        
        if (config == None or config["key"] == None or config["key"] == ""):
            self.ClientKey = clientKey
        else:
            self.ClientKey = config["key"]

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
        request_time = datetime.datetime.utcnow().isoformat()
        conn = httplib.HTTPSConnection("groker-dev.initialstate.com")
        resource = "/logs/{bucket}/{clientKey}".format(bucket=self.Bucket, clientKey=self.ClientKey)
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['User-Agent'] = 'IS PyStreamer Module'

        body = {'log': value, 'date_time': request_time, 'signal_source': signal, 'tracker_id': trackerId}
        print json.dumps(body)
        conn.set_debuglevel(1)
        conn.request("POST", resource, json.dumps(body), headers)


def getConfig():
    import os
    import ConfigParser

    home = os.path.expanduser("~")
    config_file_home_path = os.path.abspath("{home}/isstreamer.ini".format(home=home))
    config_file_local_path = os.path.abspath("{current}/isstreamer.ini".format(current=os.getcwd()))
    
    config_return = {
        "bucket": "",
        "key": ""
    }
    config_file_exists = False
    config_file_path = config_file_home_path
    if (os.path.exists(config_file_home_path)):
        config_file_path = config_file_home_path
        config_file_exists = True
    elif (os.path.exists(config_file_local_path)):
        config_file_path = config_file_local_path
        config_file_exists = True

    if (config_file_exists):
        config = ConfigParser.ConfigParser()
        config.read(config_file_path)
        if (config.has_option("isstreamer", "ClientKey")):
            config_return["key"] = config.get("isstreamer", "ClientKey")
        if (config.has_option("isstreamer", "DefaultBucket")):
            config_return["bucket"] = config.get("isstreamer", "DefaultBucket")

    return config_return



if __name__ == "__main__":
    import sys
    
    config = getConfig()
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

    log_streamer = Streamer(default_bucket, client_key)
    log_streamer.log(sys.argv[3], sys.argv[4])