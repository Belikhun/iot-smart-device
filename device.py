from logger import scope

log = scope("features")
FEATURES_INITIALIZED = False

def init_features():
	global FEATURES_INITIALIZED

	if FEATURES_INITIALIZED:
		return

	log("INFO", "Initializing board components and features...")
	import devices

	FEATURES_INITIALIZED = True
