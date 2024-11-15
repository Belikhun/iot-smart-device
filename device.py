from logger import scope
import features.utils
import client

log = scope("features")
FEATURES_INITIALIZED = False

def init_features():
	global FEATURES_INITIALIZED

	if FEATURES_INITIALIZED:
		return

	FEATURES_INITIALIZED = True

	log("INFO", "Registering feature data handler...")
	client.ws_on_data(features.utils.feature_handle_ws_data)

	log("INFO", "Initializing board components and features...")
	import devices
