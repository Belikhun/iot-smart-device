from logger import scope
from features import FeatureBase
from features.utils import get_features, push_feature_value, feature_handle_ws_data
import client

log = scope("features")
FEATURES_INITIALIZED = False

def init_features():
	global FEATURES_INITIALIZED

	if not FEATURES_INITIALIZED:
		log("INFO", "Registering feature data handler...")
		client.ws_on_data(feature_handle_ws_data)

		log("INFO", "Initializing board components and features...")
		import devices

	FEATURES_INITIALIZED = True

	log("INFO", "Pushing state of read-only features...")
	features = get_features()

	for feature in features.values():
		if feature.flags != FeatureBase.FLAG_READ:
			continue

		push_feature_value(feature)
