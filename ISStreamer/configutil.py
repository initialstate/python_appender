def getConfig(ini_file_location=None):
    import os
    import ConfigParser

    config_file_path = ""
    config_file_exists = False
    config_return = {
            "bucket": "",
            "clientKey": "",
            "pkey": "pub-c-92056f77-203d-467a-ba28-c5c8695effb6",
            "skey": "sub-c-1471fc40-4e27-11e4-b332-02ee2ddab7fe",
            "channel": "log_streamer_dev"
        }

    if (ini_file_location != None):
        if (os.path.exists(ini_file_location)):
            config_file_path = ini_file_location
            config_file_exists = True
        else:
            raise Exception("ini file path specified, but doesn't exist or is not accessable")
    else:
        home = os.path.expanduser("~")
        config_file_home_path = os.path.abspath("{home}/isstreamer.ini".format(home=home))
        config_file_local_path = os.path.abspath("{current}/isstreamer.ini".format(current=os.getcwd()))
        
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
        if (config.has_section("isstreamer.client_config")):
            if (config.has_option("isstreamer.client_config", "ClientKey")):
                config_return["clientKey"] = config.get("isstreamer.client_config", "ClientKey")
            if (config.has_option("isstreamer.client_config", "DefaultBucket")):
                config_return["bucket"] = config.get("isstreamer.client_config", "DefaultBucket")
        if (config.has_section("isstreamer.api_keys")):
            if (config.has_option("isstreamer.api_keys", "pkey")):
                config_return["pkey"] = config.get("isstreamer.api_keys", "pkey")
            if (config.has_option("isstreamer.api_keys", "skey")):
                config_return["skey"] = config.get("isstreamer.api_keys", "skey")
            if (config.has_option("isstreamer.api_keys", "channel")):
                config_return["channel"] = config.get("isstreamer.api_keys", "channel")
    else:
        raise Exception("ini can't be found or is unreadable")

    return config_return