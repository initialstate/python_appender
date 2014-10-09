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