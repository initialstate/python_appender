import pubnub

pubnub = Pubnub(publish_key="pub-c-92056f77-203d-467a-ba28-c5c8695effb6", ssl_on=True)

pubnub.publish(channel='log_streamer')