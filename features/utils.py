from logger import scope
from client import ws_do_send, ws_on_data
from features import FeatureBase
from watchdog import ws_heartbeat

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
	log("INFO", f"RCV[@{timestamp}]: {command} -> {target}")
	ws_heartbeat()

	if (command == "update"):
		id = data.get("id")
		uuid = data.get("uuid")
		value = data.get("value")
		log("INFO", f"Updating {id} [{uuid}] value from server...")

		feature = get_feature(uuid)

		if not feature:
			log("WARN", f"No feature found with UUID {uuid}, will skip updating this item")
			return

		feature.set_value(value, update_source=FeatureUpdateSource.SERVER)
		return True
	elif (command == "features"):
		ws_do_send("features", get_features_data())
		return True
	elif (command == "sync"):
		for item in data:
			id = item.get("id")
			uuid = item.get("uuid")
			value = item.get("value")
			log("INFO", f"Syncing {id} [{uuid}] value from server...")

			feature = get_feature(uuid)

			if not feature:
				log("WARN", f"No feature found with UUID {uuid}, will skip syncing this item")
				continue

			feature.set_value(value, update_source=FeatureUpdateSource.SERVER)

		return True
	elif (command == "heartbeat"):
		# Send heartbeat ACK
		ws_do_send("heartbeat")
		return True

	return False

ws_on_data(feature_handle_ws_data)
