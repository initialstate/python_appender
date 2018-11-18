def getConfig(ini_file_location=None):
    import os

    try:
        import configparser
    except ImportError:
        import ConfigParser as configparser

    config_file_path = ""
    config_file_exists = False
    config_return = {
            "bucket": "",
            "access_key": "",
            "offline_mode": "false",
            "offline_file": "./isstreamer_out.csv",
            "core_api_base": "https://api.initialstate.com",
            "stream_api_base": "https://groker.init.st"
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
        config = configparser.ConfigParser()
        config.read(config_file_path)
        if (config.has_section("isstreamer.client_config")):
            if (config.has_option("isstreamer.client_config", "access_key")):
                config_return["access_key"] = config.get("isstreamer.client_config", "access_key")
            if (config.has_option("isstreamer.client_config", "default_bucket")):
                config_return["bucket"] = config.get("isstreamer.client_config", "default_bucket")
            if (config.has_option("isstreamer.client_config", "offline_mode")):
                config_return["offline_mode"] = config.get("isstreamer.client_config", "offline_mode")
            if (config.has_option("isstreamer.client_config", "offline_file")):
                config_return["offline_file"] = config.get("isstreamer.client_config", "offline_file")
        if (config.has_section("isstreamer.api_config")):
            if (config.has_option("isstreamer.api_config", "core_api_base")):
                config_return["core_api_base"] = config.get("isstreamer.api_config", "core_api_base")
                if (not config_return["core_api_base"].startswith("https://") and not config_return["core_api_base"].startswith("http://")):
                    raise Exception("core_api_base must start with valid http:// or https://")
            if (config.has_option("isstreamer.api_config", "stream_api_base")):
                config_return["stream_api_base"] = config.get("isstreamer.api_config", "stream_api_base")
                if (not config_return["stream_api_base"].startswith("https://") and not config_return["stream_api_base"].startswith("http://")):
                    raise Exception("stream_api_base must start with valid http:// or https://")

    return config_return