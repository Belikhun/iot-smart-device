from logger import scope
from client import ws_do_send, ws_on_data
from features import FeatureBase

log = scope("features")
FEATURES_DICT: dict[str, FeatureBase] = {}
FEATURES_DATA = None

class FeatureUpdateSource:
	HARDWARE = "hw"
	SERVER = "sv"
	INTERNAL = "int"

def register_feature(feature: FeatureBase):
	global FEATURES_DICT
	log("INFO", f"Registering feature: {feature.id}, kind: {feature.__class__.__name__}")
	FEATURES_DICT[feature.uuid] = feature

def push_feature_value(feature: FeatureBase):
	value = feature.get_value()
	log("INFO", f"[{feature.id}]: PUSH {str(value)}")
	ws_do_send("update", feature.get_update_data(), feature.uuid)

def get_features_data():
	global FEATURES_DICT, FEATURES_DATA

	if FEATURES_DATA:
		return FEATURES_DATA
	
	FEATURES_DATA = []

	for feature in FEATURES_DICT.values():
		data = {
			"id": feature.id,
			"uuid": feature.uuid,
			"name": feature.name,
			"kind": feature.__class__.__name__
		}

		FEATURES_DATA.append(data)

	return FEATURES_DATA

def get_feature(uuid: str) -> FeatureBase | None:
	global FEATURES_DICT
	return FEATURES_DICT.get(uuid)

def feature_handle_ws_data(recv_data: dict):
	if not recv_data.get("command") or not recv_data.get("target") or not recv_data.get("timestamp"):
		raise ValueError("Not a valid packet")

	command = recv_data.get("command")
	target = recv_data.get("target")
	data = recv_data.get("data")
	timestamp = recv_data.get("timestamp")
	log("INFO", f"RCV[{target}@{timestamp}]: {command}")

	if (command == "update"):
		feature = get_feature(target)

		if not feature:
			log("WARN", f"No feature found with ID {target}")

		feature.set_value(data, update_source=FeatureUpdateSource.SERVER)
	elif (command == "features"):
		ws_do_send("features", get_features_data())

ws_on_data(feature_handle_ws_data)
