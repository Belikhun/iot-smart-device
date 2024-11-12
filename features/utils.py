from logger import scope
from client import ws_do_send
from features import FeatureBase

log = scope("features")
FEATURES_DICT = {}

class FeatureUpdateSource:
	HARDWARE = "hw"
	SERVER = "sv"
	INTERNAL = "int"

def register_feature(feature: FeatureBase):
	global FEATURES_DICT
	log("INFO", f"Registering feature: {feature.id}, kind: {feature.__class__.__name__}")
	FEATURES_DICT[feature.id] = feature

def push_feature_value(feature: FeatureBase):
	value = feature.get_value()
	log("INFO", f"[{feature.id}]: PUSH {str(value)}")
	ws_do_send("update", feature.get_update_data(), feature.uuid)

def get_features():
	global FEATURES_DICT
	return FEATURES_DICT

def get_feature(id: str) -> FeatureBase | None:
	global FEATURES_DICT
	return FEATURES_DICT.get(id)
